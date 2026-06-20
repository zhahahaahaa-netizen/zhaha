// sync.js
import "dotenv/config";
import fs from "fs";
import { ethers } from "ethers";
import {
  Indexer,
  Batcher,
  KvClient,
  getFlowContract
} from "@0gfoundation/0g-storage-ts-sdk";

const RPC_URL = process.env.RPC_URL;
const INDEXER_RPC = process.env.INDEXER_RPC;
const PRIVATE_KEY = process.env.PRIVATE_KEY;

const STREAM_ID =
  process.env.STREAM_ID ||
  "0x0c2a2d101aba16831fd325bb3b20441dafc45a769f05ec4d7e5293ba45c5f1ba";

const SETTINGS_PATH = process.argv[3] || "./settings.json";
const SETTINGS_KEY = "settings";

function requireEnv(name) {
  const value = process.env[name];

  if (!value) {
    console.error(`Missing ${name} in .env`);
    process.exit(1);
  }

  return value;
}

async function getSigner() {
  const provider = new ethers.JsonRpcProvider(
    requireEnv("RPC_URL")
  );

  return new ethers.Wallet(
    requireEnv("PRIVATE_KEY"),
    provider
  );
}

async function push() {
  if (!fs.existsSync(SETTINGS_PATH)) {
    console.error(`Missing file: ${SETTINGS_PATH}`);
    process.exit(1);
  }

  const signer = await getSigner();
  const indexer = new Indexer(requireEnv("INDEXER_RPC"));

  const raw = fs.readFileSync(
    SETTINGS_PATH,
    "utf8"
  );

  const [nodes, nodeErr] = await indexer.selectNodes(1);
  console.log("SELECTED NODE:");
  console.dir(nodes[0], { depth: 3 });

  if (nodeErr) {
    console.error("Node selection failed:", nodeErr);
    process.exit(1);
  }

  const status = await nodes[0].getStatus();

  console.log("NETWORK IDENTITY:");
  console.dir(status.networkIdentity, {
    depth: null
  });

  const flowAddress =
    status?.networkIdentity?.flowAddress;

  if (!flowAddress) {
    throw new Error(
      "flowAddress missing from node status"
    );
  }

  const flow = getFlowContract(
    flowAddress,
    signer
  );

  const batcher = new Batcher(
    1,
    nodes,
    flow,
    RPC_URL
  );

  const keyBytes = Uint8Array.from(
    Buffer.from(SETTINGS_KEY, "utf8")
  );

  const valueBytes = Uint8Array.from(
    Buffer.from(raw, "utf8")
  );

  batcher.streamDataBuilder.set(
    STREAM_ID,
    keyBytes,
    valueBytes
  );

  const [tx, batchErr] = await batcher.exec();

  if (batchErr) {
    console.error("Batch execution error:");
    console.error(batchErr);
    process.exit(1);
  }

  console.log("✅ Push successful");
  console.log(tx);
}

async function pull() {
  const KV_RPC = process.env.KV_RPC || "http://3.101.147.150:6789";

  const kvClient = new KvClient(KV_RPC);

  const keyBytes = Uint8Array.from(
  Buffer.from("settings", "utf8")
);

const value = await kvClient.getValue(
  STREAM_ID,
  keyBytes
);

console.log(value);

  if (!value) {
    console.error("No data found");
    process.exit(1);
  }

  fs.writeFileSync(SETTINGS_PATH, value);

  console.log(
    "✅ Pulled settings ->",
    SETTINGS_PATH
  );
}
const mode = process.argv[2];

if (mode === "push") {
  push().catch((err) => {
    console.error(err);
    process.exit(1);
  });
} else if (mode === "pull") {
  pull().catch((err) => {
    console.error(err);
    process.exit(1);
  });
} else {
  console.log(
    "Usage: node sync.js [push|pull] [settings-file]"
  );
}