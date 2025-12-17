# gRPC 应用开发

> 使用 gRPC 构建高性能 RPC 服务

## 1. gRPC 概述

gRPC 是高性能、跨语言的 RPC 框架：
- 基于 HTTP/2
- 使用 Protocol Buffers
- 支持流式传输
- 跨语言支持

## 2. 定义服务

### 2.1 编写 .proto 文件

```protobuf
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);
}

message UserRequest {
  int32 id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}
```

### 2.2 生成代码

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
```

## 3. 实现服务端

```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_pb2.UserResponse(
            id=request.id,
            name="Alice",
            email="alice@example.com"
        )
    
    def CreateUser(self, request, context):
        # 创建用户逻辑
        return user_pb2.UserResponse(
            id=1,
            name=request.name,
            email=request.email
        )
    
    def ListUsers(self, request, context):
        # 流式返回
        for i in range(10):
            yield user_pb2.UserResponse(
                id=i,
                name=f"User{i}",
                email=f"user{i}@example.com"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

## 4. 实现客户端

```python
import grpc
import user_pb2
import user_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        
        # 调用服务
        response = stub.GetUser(user_pb2.UserRequest(id=1))
        print(f"用户: {response.name}")
        
        # 流式调用
        responses = stub.ListUsers(user_pb2.ListUsersRequest(page=1, page_size=10))
        for response in responses:
            print(f"用户: {response.name}")

if __name__ == '__main__':
    run()
```

## 5. 总结

gRPC 应用开发要点：
- **Protocol Buffers**：定义服务接口
- **服务端实现**：实现服务方法
- **客户端调用**：使用生成的客户端代码
- **流式传输**：支持单向和双向流
- **跨语言**：支持多种编程语言

gRPC 适合构建高性能的微服务系统。

