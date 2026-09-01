import { network } from "hardhat";

const { viem } = await network.connect();

const godsEye = await viem.getContractAt(
  "GodsEye",
  "0x5fbdb2315678afecb367f032d93f642f64180aa3"
);

const realImageHash =
  "fac4cadb6740ba7b8e2e484ee0aee77e3eff4db55f991c3b7cff976b0336bb89";

console.log("\n========== GOD'S EYE ==========");
console.log("       INTEGRITY CHECK");
console.log("================================\n");

const genuine = await godsEye.read.verifyRecord([
  1n,
  realImageHash,
  "MODEL_XYZ456",
  "INFERENCE_DEF789",
]);

console.log("Test 1 — Original Data");
console.log("Result:", genuine ? "✅ VERIFIED" : "❌ TAMPERED");

const tampered = await godsEye.read.verifyRecord([
  1n,
  "THIS_IS_A_CHANGED_IMAGE_HASH",
  "MODEL_XYZ456",
  "INFERENCE_DEF789",
]);

console.log("\nTest 2 — Modified Image");
console.log("Result:", tampered ? "✅ VERIFIED" : "❌ TAMPERED");

console.log("\n================================");