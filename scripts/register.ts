import { network } from "hardhat";

const { viem } = await network.connect();

const godsEye = await viem.getContractAt(
  "GodsEye",
  "0x5fbdb2315678afecb367f032d93f642f64180aa3"
);

const imageHash =
  "fac4cadb6740ba7b8e2e484ee0aee77e3eff4db55f991c3b7cff976b0336bb89";

console.log("Registering real image integrity record...");

const txHash = await godsEye.write.registerRecord([
  imageHash,
  "MODEL_XYZ456",
  "INFERENCE_DEF789",
  "Company_A",
]);

console.log("Transaction:", txHash);
console.log("Real image hash registered successfully!");