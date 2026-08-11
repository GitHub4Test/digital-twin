from concurrent import futures

import grpc

from sensor_service.generated.sensor.v1 import sensor_pb2_grpc
from sensor_service.sensor_servicer import SensorServicer


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sensor_pb2_grpc.add_SensorServiceServicer_to_server(SensorServicer(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Sensor service running on port 50052")
    server.wait_for_termination()


if __name__ == "__main__":
    run()