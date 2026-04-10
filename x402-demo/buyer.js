/**
 * x402 买方 Agent（API 调用方）
 *
 * 这个脚本模拟一个 AI Agent 调用付费 API 的过程：
 * 1. 发请求 → 收到 402
 * 2. 自动用钱包签名支付
 * 3. 带签名重新请求 → 拿到数据
 *
 * 用法：npm run buyer（确保卖方服务已启动）
 */

import { createPublicClient, createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { baseSepolia } from "viem/chains";
import { payForRequest } from "@x402/client";
import dotenv from "dotenv";

dotenv.config();

// === 配置 ===
const SELLER_URL = `http://localhost:${process.env.PORT || 4402}/api/weather`;
const BUYER_PRIVATE_KEY = process.env.BUYER_PRIVATE_KEY;

if (!BUYER_PRIVATE_KEY) {
  console.error("❌ 请先在 .env 中设置 BUYER_PRIVATE_KEY");
  console.error("   运行 node setup-wallet.js 生成钱包");
  process.exit(1);
}

// === 创建钱包客户端 ===
// 用买方的私钥创建一个钱包，用于签名支付
const account = privateKeyToAccount(BUYER_PRIVATE_KEY);
const walletClient = createWalletClient({
  account,
  chain: baseSepolia,
  transport: http(),
});
const publicClient = createPublicClient({
  chain: baseSepolia,
  transport: http(),
});

async function main() {
  console.log("");
  console.log("🤖 x402 买方 Agent 启动");
  console.log(`   钱包地址：${account.address}`);
  console.log(`   目标 API：${SELLER_URL}`);
  console.log("");

  // === 第一步：直接请求（会收到 402） ===
  console.log("📡 第一步：发送普通请求...");
  const firstResponse = await fetch(SELLER_URL);
  console.log(`   响应状态：${firstResponse.status}`);

  if (firstResponse.status === 402) {
    console.log("   💰 收到 HTTP 402 - 需要付费！");

    // 打印支付要求（从响应头中解析）
    const paymentHeader = firstResponse.headers.get("x-payment");
    if (paymentHeader) {
      try {
        const paymentInfo = JSON.parse(paymentHeader);
        console.log("   支付要求：");
        console.log(`     金额：${paymentInfo.maxAmountRequired} 最小单位`);
        console.log(`     折合：$${Number(paymentInfo.maxAmountRequired) / 1_000_000} USDC`);
        console.log(`     收款地址：${paymentInfo.payTo}`);
        console.log(`     网络：${paymentInfo.network}`);
      } catch {
        console.log(`   支付信息：${paymentHeader}`);
      }
    }
    console.log("");

    // === 第二步：使用 x402 客户端自动处理支付 ===
    console.log("🔐 第二步：签名支付并重新请求...");
    console.log("   （Agent 自动完成：解析 402 → 签名 → 重新请求）");
    console.log("");

    try {
      // payForRequest 会自动：
      // 1. 解析 402 响应中的支付要求
      // 2. 用钱包私钥签名 EIP-712 支付授权
      // 3. 带着签名重新发送请求
      const paidResponse = await payForRequest(
        SELLER_URL,
        {},  // 请求选项（GET 请求不需要额外选项）
        walletClient,
        publicClient,
      );

      if (paidResponse.ok) {
        const data = await paidResponse.json();
        console.log("✅ 第三步：支付成功，收到数据！");
        console.log("");
        console.log("📊 天气数据：");
        console.log(`   城市：${data.city}`);
        console.log(`   温度：${data.temperature}`);
        console.log(`   天气：${data.weather}`);
        console.log(`   湿度：${data.humidity}`);
        console.log(`   风力：${data.wind}`);
        console.log(`   时间：${data.timestamp}`);
        console.log("");
        console.log(`   ${data.message}`);
      } else {
        console.error(`❌ 支付后请求失败：${paidResponse.status}`);
        const errorText = await paidResponse.text();
        console.error(`   错误信息：${errorText}`);
      }
    } catch (error) {
      console.error("❌ 支付过程出错：");
      console.error(`   ${error.message}`);
      console.error("");

      // 常见错误提示
      if (error.message.includes("insufficient")) {
        console.error("💡 可能原因：买方钱包 USDC 余额不足");
        console.error("   解决：去 https://faucet.circle.com 领取测试 USDC");
        console.error(`   买方地址：${account.address}`);
      }
    }
  } else if (firstResponse.ok) {
    // 如果第一次请求就成功了（不应该发生，除非中间件没生效）
    const data = await firstResponse.json();
    console.log("   ⚠️ 请求直接成功了（没有触发 402），数据：");
    console.log(data);
  } else {
    console.error(`   ❌ 意外的响应状态：${firstResponse.status}`);
  }

  console.log("");
  console.log("=== Demo 结束 ===");
}

main().catch(console.error);
