import { createPublicClient, createWalletClient, http } from "viem";
import { hardhat } from "viem/chains";
import fs from "fs";
import path from "path";

async function main() {
  const rpcUrl = "http://127.0.0.1:8545";

  const publicClient = createPublicClient({
    chain: hardhat,
    transport: http(rpcUrl),
  });

  const walletClient = createWalletClient({
    chain: hardhat,
    transport: http(rpcUrl),
  });

  const [account] = await walletClient.getAddresses();

  const artifactPath = path.resolve("./artifacts/contracts/GodsEye.sol/GodsEye.json");
  if (!fs.existsSync(artifactPath)) {
    throw new Error("Artifact not found! Run 'npx.cmd hardhat compile' first.");
  }
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf-8"));

  console.log(`Deploying GodsEye from account: ${account}...`);

  const hash = await walletClient.deployContract({
    abi: artifact.abi,
    bytecode: artifact.bytecode,
    account: account,
  });

  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log(`GodsEye contract deployed to: ${receipt.contractAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});