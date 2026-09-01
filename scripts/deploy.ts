import { network } from "hardhat";

const { viem } = await network.connect();

const godsEye = await viem.deployContract("GodsEye");

console.log("God's Eye deployed successfully!");
console.log("Contract address:", godsEye.address);