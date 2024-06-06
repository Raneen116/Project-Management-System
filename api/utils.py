from rest_framework.response import Response


def custom_response(data={}, message="", status=200):
    response = {"data": data, "message": message, "status": status}

    return Response(data=response, status=status)
