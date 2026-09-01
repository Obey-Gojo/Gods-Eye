import { network } from "hardhat";

const { viem } = await network.connect();

const godsEye = await viem.getContractAt(
  "GodsEye",
  "0x5fbdb2315678afecb367f032d93f642f64180aa3"
);

console.log("\n========== GOD'S EYE ==========");
console.log("      BLOCKCHAIN RECORD");
console.log("================================\n");

const record = await godsEye.read.getRecord([1n]);

console.log("Record ID:       1");
console.log("Image Hash:     ", record[0]);
console.log("Model Hash:     ", record[1]);
console.log("Inference Hash: ", record[2]);
console.log("Contributor:    ", record[3]);
console.log("Timestamp:      ", record[4].toString());

console.log("\n================================");