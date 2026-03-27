# URLSession 与网络请求

> Author: Walter Wang

## 1. 基础 GET 请求

```swift
func fetchUsers() async throws -> [User] {
    let url = URL(string: "https://api.example.com/users")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse
    }
    return try JSONDecoder().decode([User].self, from: data)
}
```

## 2. POST 请求

```swift
func createUser(_ user: CreateUserRequest) async throws -> User {
    var request = URLRequest(url: URL(string: "https://api.example.com/users")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.httpBody = try JSONEncoder().encode(user)
    request.timeoutInterval = 30

    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(User.self, from: data)
}
```

## 3. 下载任务

```swift
func downloadFile(from url: URL) async throws -> URL {
    let (localURL, response) = try await URLSession.shared.download(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.downloadFailed
    }

    // 移动到 Documents 目录
    let docsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
    let destURL = docsURL.appendingPathComponent(url.lastPathComponent)
    try FileManager.default.moveItem(at: localURL, to: destURL)
    return destURL
}

// 带进度的下载
class DownloadManager: NSObject, URLSessionDownloadDelegate {
    func startDownload(url: URL) {
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
        session.downloadTask(with: url).resume()
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didWriteData bytesWritten: Int64, totalBytesWritten: Int64,
                    totalBytesExpectedToWrite: Int64) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        DispatchQueue.main.async { self.updateProgress(progress) }
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didFinishDownloadingTo location: URL) {
        // 处理下载完成
    }
}
```

## 4. 上传任务

```swift
func uploadImage(_ image: UIImage) async throws {
    let url = URL(string: "https://api.example.com/upload")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

    var body = Data()
    body.append("--\(boundary)\r\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"photo.jpg\"\r\n".data(using: .utf8)!)
    body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
    body.append(image.jpegData(compressionQuality: 0.8)!)
    body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

    let (_, response) = try await URLSession.shared.upload(for: request, from: body)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw NetworkError.uploadFailed
    }
}
```

## 5. URLSession 配置

```swift
// 自定义配置
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 30
config.waitsForConnectivity = true
config.httpAdditionalHeaders = ["Accept": "application/json"]

let session = URLSession(configuration: config)

// 后台下载配置
let bgConfig = URLSessionConfiguration.background(withIdentifier: "com.app.download")
bgConfig.isDiscretionary = true
bgConfig.sessionSendsLaunchEvents = true
```

## 6. Certificate Pinning

```swift
class PinnedSessionDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        let serverCertData = SecCertificateCopyData(certificate) as Data
        let localCertData = NSData(contentsOfFile: Bundle.main.path(forResource: "cert", ofType: "cer")!)! as Data

        if serverCertData == localCertData {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```
