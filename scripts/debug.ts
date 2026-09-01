import { network } from "hardhat";

const { viem } = await network.connect();

const godsEye = await viem.getContractAt(
  "GodsEye",
  "0x5fbdb2315678afecb367f032d93f642f64180aa3"
);

const record = await godsEye.read.getRecord([1n]);

console.log("IMAGE STORED:");
console.log(record[0]);

console.log("\nIMAGE TEST:");
console.log(
  "fac4cadb6740ba7b8e2e484ee0aee77e3eff4db55f991c3b7cff976b0336bb89"
);

console.log("\nMODEL STORED:");
console.log(record[1]);

console.log("\nINFERENCE STORED:");
console.log(record[2]);

console.log("\nDIRECT COMPARISON:");

console.log(
  "Image:",
  record[0] ===
    "fac4cadb6740ba7b8e2e484ee0aee77e3eff4db55f991c3b7cff976b0336bb89"
);

console.log("Model:", record[1] === "MODEL_XYZ456");

console.log("Inference:", record[2] === "INFERENCE_DEF789");