from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status


from apps.client.api.serializers import ClientSerializer
from apps.client.models import Client
from apps.employee.api.serializers import EmployeeSerializer
from apps.employee.models import CategoryEmployee, Employee
from apps.operation.api.serializers import OperationSerializer
from apps.operation.models import Operation
from apps.service.api.serializers import (
    ServiceSerializer,
    ServicesClientMonthlyInvoiceSerializer,
)
from apps.service.models import Service, ServicesClientMonthlyInvoice


class ОperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    http_method_names = ["get", "post", "delete", "update"]

    @action(detail=False, methods=["post"], url_path=r"operation_save")
    def operation_save(self, request, *args, **kwargs):
        try:
            data = request.data
            # СОХПРАНЕНИЕ ОПЕРАЦИИ
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                obj = serializer.save()

            # операциоо по услагам счетов
            if "monthly_bill" in data:
                servise_month = ServicesClientMonthlyInvoice.objects.get(
                    id=data["monthly_bill"]
                )
                # входящая операция
                if data["bank_in"] == "4":
                    servise_month.operations_add_all = (
                        servise_month.operations_add_all + float(data["amount"])
                    )
                    servise_month.operations_add_diff_all = (
                        servise_month.operations_add_diff_all + float(data["amount"])
                    )
                    if data["bank_to"] == "1":
                        if servise_month.operations_add_ip:
                            servise_month.operations_add_ip = (
                                servise_month.operations_add_ip + float(data["amount"])
                            )
                        else:
                            servise_month.operations_add_ip = float(data["amount"])

                    elif data["bank_to"] == "2":
                        if servise_month.operations_add_ооо:
                            servise_month.operations_add_ооо = (
                                servise_month.operations_add_ооо + float(data["amount"])
                            )
                        else:
                            servise_month.operations_add_ооо = float(data["amount"])
                    elif data["bank_to"] == "3":
                        if servise_month.operations_add_nal:
                            servise_month.operations_add_nal = (
                                servise_month.operations_add_nal + float(data["amount"])
                            )
                        else:
                            servise_month.operations_add_nal = float(data["amount"])
                    servise_month.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

        # serializer = self.serializer_class(data=data)
        # idBill = data['monthly_bill']

        # # operation = Operation.objects.filter(
        # #     monthly_bill=idBill, type_operation='entry').aggregate(total=Sum('amount', default=0))

        # if serializer.is_valid():
        #     obj = serializer.save()
        #     billNeedSumEntry = ServicesMonthlyBill.objects.get(
        #         id=idBill)
        #     operation = Operation.objects.filter(
        #         monthly_bill=idBill, type_operation='entry').aggregate(total=Sum('amount', default=0))

        #     if operation['total'] == billNeedSumEntry.contract_sum:
        #         billNeedSumEntry.chekin_sum_entrees = True
        #         billNeedSumEntry.save()
        #     else:
        #         billNeedSumEntry.chekin_sum_entrees = False
        #         billNeedSumEntry.save()

        #     return Response(serializer.data, status=status.HTTP_201_CREATED)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path=r"operation_entry_list")
    def operation_entry_list(self, request, *args, **kwargs):
        data = request.data
        queryset = Operation.objects.filter(
            monthly_bill=data["monthly_bill"],
            bank_in=data["bank_in"],
        )
        print(queryset)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path=r"operation_delete")
    def operation_delete(self, request, *args, **kwargs):
        try:
            data = request.data
            operation = Operation.objects.get(id=data["id"])
            print(operation)
            print(operation.monthly_bill)
            # операциоо по услагам счетов
            if operation.monthly_bill:
                print(0000)
                servise_month = ServicesClientMonthlyInvoice.objects.get(
                    id=operation.monthly_bill.id
                )
                print(1111)
                # входящая операция
                if operation.bank_in == 4:
                    print("operation.bank_in == 4")
                    servise_month.operations_add_all = (
                        servise_month.operations_add_all - operation.amount
                    )
                    if operation.bank_to == 1:
                        print("operation.bank_to == 1")
                        if servise_month.operations_add_ip != operation.amount:
                            servise_month.operations_add_ip = (
                                servise_month.operations_add_ip - operation.amount
                            )
                        else:
                            servise_month.operations_add_ip = None

                    elif operation.bank_to == 2:
                        print("operation.bank_to == 2")
                        if servise_month.operations_add_ооо != operation.amount:
                            servise_month.operations_add_ооо = (
                                servise_month.operations_add_ооо - operation.amount
                            )
                        else:
                            servise_month.operations_add_ооо = None
                    elif operation.bank_to == 3:
                        print("operation.bank_to == 3")
                        if servise_month.operations_add_nal != operation.amount:
                            servise_month.operations_add_nal = (
                                servise_month.operations_add_nal - operation.amount
                            )
                        else:
                            servise_month.operations_add_nal = None
                    servise_month.save()

            operation.delete()
            print(999999)
            context = {
                "result": "ok"
            }
            return Response(context, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
