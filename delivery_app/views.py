from operator import itemgetter
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from delivery_app.models import DeliveryInfoModel
from delivery_app.serializers import DeliverySerializer
from itertools import groupby
from datetime import datetime
import pytz

@api_view(['GET'])
def delivery_list_v2(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        date = request.query_params.get("date")
        query = " AND dis.billing_date = CURRENT_DATE() "
        if date != "":
            query = " AND dis.billing_date = '"+date+"' "
        if d_type == 'All':
            query = query + ""
        elif d_type == 'Remaining':
            query = query + "AND d.delivery_status IS NULL"
        else:
            query = query + "AND d.delivery_status = '"+d_type+"'"

        sql = "SELECT dis.*,IFNULL(rs.description, 'No Route Name') AS route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "d.id,dl.id list_id,d.transport_type," \
                "dl.delivery_quantity,dl.delivery_net_val,dl.return_quantity,dl.return_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "LEFT JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN (SELECT DISTINCT customer_id, latitude, longitude FROM rdl_customer_location LIMIT 1) cl ON sis.partner = cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr " \
                "WHERE dis.da_code = '%s' "+query+" ;"

    data_list = DeliveryInfoModel.objects.raw(sql,[sap_id])
    if len(data_list) == 0:
        return Response({"success": False, "message": "Data not available!"}, status=status.HTTP_200_OK)
    else:
        an_iterator = groupby(data_list, lambda x : x.billing_doc_no)
        data = []
        for key, group in an_iterator:
            key_and_group = {key : list(group)}
            sub_data = []
            for item in key_and_group[key]:
                rec_qty = 0
                if item.delivery_quantity is not None:
                    rec_qty = item.delivery_quantity
                rec_net_val = 0
                if item.delivery_net_val is not None:
                    rec_net_val = item.delivery_net_val

                ret_qty = 0
                if item.return_quantity is not None:
                    ret_qty = item.return_quantity
                ret_net_val = 0
                if item.return_net_val is not None:
                    ret_net_val = item.return_net_val

                sub_data.append({
                    "id": item.list_id,
                    "matnr": item.matnr,
                    "quantity": item.quantity,
                    "tp": item.tp,
                    "vat": item.vat,
                    "net_val": item.net_val,
                    "batch": item.batch,
                    "material_name": item.material_name,
                    "brand_description": item.brand_description,
                    "brand_name": item.brand_name,
                    "delivery_quantity": rec_qty,
                    "delivery_net_val": rec_net_val,
                    "return_quantity": ret_qty,
                    "return_net_val": ret_net_val,
                })

                cash_collection = 0
                if key_and_group[key][0].cash_collection is not None:
                    cash_collection = key_and_group[key][0].cash_collection

                
            main_data = {
                "id": key_and_group[key][0].id,
                "billing_doc_no": key_and_group[key][0].billing_doc_no,
                "billing_date": key_and_group[key][0].billing_date,
                "route_code": key_and_group[key][0].route,
                "route_name": key_and_group[key][0].route_name,
                "da_code": key_and_group[key][0].da_code,
                "da_name": key_and_group[key][0].da_name,
                "partner": key_and_group[key][0].partner,
                "customer_name": key_and_group[key][0].customer_name,
                "customer_address": key_and_group[key][0].customer_address,
                "customer_mobile": key_and_group[key][0].customer_mobile,
                "latitude": key_and_group[key][0].latitude,
                "longitude": key_and_group[key][0].longitude,
                "delivery_status": key_and_group[key][0].delivery_status,
                "cash_collection": cash_collection,
                "cash_collection_status": key_and_group[key][0].cash_collection_status,
                "gate_pass_no": key_and_group[key][0].gate_pass_no,
                "vehicle_no": key_and_group[key][0].vehicle_no,
                "transport_type": key_and_group[key][0].transport_type,
                "product_list": sub_data
            }
            data.append(main_data)
            
            key_func = itemgetter('billing_date', 'partner')
            sorted_data = sorted(data, key=key_func)
            grouped_data = {key: list(group) for key, group in groupby(sorted_data, key=key_func)}
            customer_data = []
            for (billing_date, partner), group in grouped_data.items():
                customer_data.append({
                    "billing_date": group[0]['billing_date'],
                    "route_code": group[0]['route_code'],
                    "route_name": group[0]['route_name'],
                    "da_code": group[0]['da_code'],
                    "da_name": group[0]['da_name'],
                    "partner": group[0]['partner'],
                    "customer_name": group[0]['customer_name'],
                    "customer_address": group[0]['customer_address'],
                    "customer_mobile": group[0]['customer_mobile'],
                    "latitude": group[0]['latitude'],
                    "longitude": group[0]['longitude'],
                    "gate_pass_no": group[0]['gate_pass_no'],
                    "invoice_list": group,
            }) 

        return Response({"success": True, "result": customer_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def delivery_list(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        query = ""
        if d_type == 'All':
            query = ""
        elif d_type == 'Remaining':
            query = "AND d.delivery_status IS NULL"
        else:
            query = "AND d.delivery_status = '"+d_type+"'"

        sql = "SELECT dis.*,rs.description route_name, " \
                "sis.billing_type,sis.partner,sis.matnr,sis.quantity,sis.tp,sis.vat,sis.net_val,sis.assigment,sis.gate_pass_no,sis.batch,sis.plant,sis.team,sis.created_on, " \
                "m.material_name,m.brand_description,m.brand_name, " \
                "CONCAT(c.name1,c.name2) customer_name,CONCAT(c.street,c.street1,c.street2) customer_address,c.mobile_no customer_mobile, " \
                "cl.latitude,cl.longitude, " \
                "d.id,dl.id list_id,d.transport_type," \
                "dl.delivery_quantity,dl.delivery_net_val,IF(d.delivery_status IS NULL,'Pending',d.delivery_status) delivery_status,d.cash_collection,IF(d.cash_collection_status IS NULL,'Pending',d.cash_collection_status) cash_collection_status " \
                "FROM rdl_delivery_info_sap dis " \
                "INNER JOIN rdl_route_sap rs ON dis.route=rs.route " \
                "INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no " \
                "INNER JOIN rpl_material m ON sis.matnr=m.matnr " \
                "INNER JOIN rpl_customer c ON sis.partner=c.partner " \
                "LEFT JOIN rdl_customer_location cl ON sis.partner=cl.customer_id " \
                "LEFT JOIN rdl_delivery d ON sis.billing_doc_no=d.billing_doc_no " \
                "LEFT JOIN rdl_delivery_list dl ON d.id=dl.delivery_id AND sis.matnr=dl.matnr " \
                "WHERE dis.billing_date = CURRENT_DATE() AND dis.da_code = '%s' "+query+" ;"


    data_list = DeliveryInfoModel.objects.raw(sql,[sap_id])
    an_iterator = groupby(data_list, lambda x : x.billing_doc_no)
    data = []
    for key, group in an_iterator:
        key_and_group = {key : list(group)}
        sub_data = []
        for item in key_and_group[key]:
            rec_qty = 0
            if item.delivery_quantity is not None:
                rec_qty = item.delivery_quantity
            rec_net_val = 0
            if item.delivery_net_val is not None:
                rec_net_val = item.delivery_net_val

            sub_data.append({
                "id": item.list_id,
                "matnr": item.matnr,
                "quantity": item.quantity,
                "tp": item.tp,
                "vat": item.vat,
                "net_val": item.net_val,
                "batch": item.batch,
                "material_name": item.material_name,
                "brand_description": item.brand_description,
                "brand_name": item.brand_name,
                "delivery_quantity": rec_qty,
                "delivery_net_val": rec_net_val,
            })

            cash_collection = 0
            if key_and_group[key][0].cash_collection is not None:
                cash_collection = key_and_group[key][0].cash_collection

            
        main_data = {
            "id": key_and_group[key][0].id,
            "billing_doc_no": key_and_group[key][0].billing_doc_no,
            "billing_date": key_and_group[key][0].billing_date,
            "route_code": key_and_group[key][0].route,
            "route_name": key_and_group[key][0].route_name,
            "da_code": key_and_group[key][0].da_code,
            "da_name": key_and_group[key][0].da_name,
            "partner": key_and_group[key][0].partner,
            "customer_name": key_and_group[key][0].customer_name,
            "customer_address": key_and_group[key][0].customer_address,
            "customer_mobile": key_and_group[key][0].customer_mobile,
            "latitude": key_and_group[key][0].latitude,
            "longitude": key_and_group[key][0].longitude,
            "delivery_status": key_and_group[key][0].delivery_status,
            "cash_collection": cash_collection,
            "cash_collection_status": key_and_group[key][0].cash_collection_status,
            "gate_pass_no": key_and_group[key][0].gate_pass_no,
            "vehicle_no": key_and_group[key][0].vehicle_no,
            "transport_type": key_and_group[key][0].transport_type,
            "product_list": sub_data
        }
        data.append(main_data)
    return Response({"success": True, "result": data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def delivery_save(request):
    if request.method == 'POST':
        tz_Dhaka = pytz.timezone('Asia/Dhaka')
        productList = []
        for item in request.data['deliverys']:
            productList.append({
                "batch": item["batch"],
                "delivery_net_val": round(item["delivery_net_val"],2),
                "delivery_quantity": item["delivery_quantity"],
                "matnr": item["matnr"],
                "net_val": round(item["net_val"],2),
                "quantity": item["quantity"],
                "return_net_val": round(item["return_net_val"],2),
                "return_quantity": item["return_quantity"],
                "tp": item["tp"],
                "vat": item["vat"],
            })
        main_data = {
            "billing_date": request.data['billing_date'],
            "billing_doc_no": request.data['billing_doc_no'],
            "cash_collection": request.data['cash_collection'],
            "da_code": request.data['da_code'],
            "delivery_latitude": request.data['delivery_latitude'],
            "delivery_longitude": request.data['delivery_longitude'],
            "delivery_status": request.data['delivery_status'],
            "gate_pass_no": request.data['gate_pass_no'],
            "last_status": request.data['last_status'],
            "partner": request.data['partner'],
            "route_code": request.data['route_code'],
            "transport_type": request.data['transport_type'],
            "type": request.data['type'],
            "vehicle_no": request.data['vehicle_no'],
            "deliverys": productList,
        }

        serializer = DeliverySerializer(data=main_data, partial=True)
        if serializer.is_valid():
            if request.data.get('type') == "delivery":
                serializer.validated_data['delivery_date_time'] = datetime.now(tz_Dhaka)
            if request.data.get('type') == "cash_collection":
                serializer.validated_data['cash_collection_date_time'] = datetime.now(tz_Dhaka)
            if request.data.get('type') == "return":
                serializer.validated_data['return_date_time'] = datetime.now(tz_Dhaka)
            serializer.save()
            return Response({"success": True, "result": serializer.data}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)