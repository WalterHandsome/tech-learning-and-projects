/**
 * x402 卖方服务（API 提供者）
 *
 * 这是一个普通的 Express API 服务，加了 x402 付费墙中间件。
 * 未付费的请求会收到 HTTP 402，付费后返回数据。
 *
 * 用法：npm run seller
 */

import express from "express";
import { paymentMiddleware } from "@x402/express";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4402;

// 卖方收款地址（从 .env 读取）
const sellerAddress = process.env.SELLER_WALLET_ADDRESS;

if (!sellerAddress) {
  console.error("❌ 请先在 .env 中设置 SELLER_WALLET_ADDRESS");
  console.error("   运行 node setup-wallet.js 生成钱包");
  process.exit(1);
}

// Facilitator 地址（测试网用 x402.org 的免费服务）
const facilitatorUrl = "https://x402.org/facilitator";

// === 付费 API 路由 ===

// 这个路由需要付费才能访问
// 价格：$0.001（即 1000 个 USDC 最小单位）
app.get(
  "/api/weather",
  // x402 中间件：自动处理 402 响应和支付验证
  paymentMiddleware(
    sellerAddress,       // 收款地址
    {
      // 定价：每次调用 $0.001 USDC
      maxAmountRequired: 1000,  // 1000 = 0.001 USDC（6 位小数）
      network: "base-sepolia",  // 测试网
      asset: "USDC",
    },
    {
      url: facilitatorUrl,      // Facilitator 地址
    }
  ),
  // 支付验证通过后，执行业务逻辑
  (req, res) => {
    console.log("✅ 收到付费请求，返回天气数据");
    res.json({
      city: "上海",
      temperature: "26°C",
      weather: "晴天",
      humidity: "65%",
      wind: "东南风 3 级",
      timestamp: new Date().toISOString(),
      message: "🎉 你成功通过 x402 协议付费获取了这条数据！",
    });
  }
);

// 免费路由（用于测试服务是否正常运行）
app.get("/", (req, res) => {
  res.json({
    service: "x402 Demo - 天气 API",
    status: "running",
    endpoints: {
      "/": "免费 - 服务状态（你现在看到的）",
      "/api/weather": "付费 - 天气数据（$0.001 USDC/次）",
    },
    network: "Base Sepolia（测试网）",
  });
});

app.listen(PORT, () => {
  console.log("");
  console.log("🏪 x402 卖方服务已启动");
  console.log(`   地址：http://localhost:${PORT}`);
  console.log(`   收款钱包：${sellerAddress}`);
  console.log(`   Facilitator：${facilitatorUrl}`);
  console.log("");
  console.log("📡 路由：");
  console.log(`   GET http://localhost:${PORT}/          → 免费（服务状态）`);
  console.log(`   GET http://localhost:${PORT}/api/weather → 付费（$0.001 USDC）`);
  console.log("");
  console.log("等待买方请求...");
});
