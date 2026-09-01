import { createHash } from "crypto";
import { readFileSync } from "fs";

const filePath = "test-data/OIP.jpg";
const file = readFileSync(filePath);

const hash = createHash("sha256")
    .update(file)
    .digest("hex");

console.log("\n========== GOD'S EYE ==========");
console.log("        FILE INTEGRITY");
console.log("================================");
console.log("File:", filePath);
console.log("SHA-256:", hash);
console.log("================================\n");