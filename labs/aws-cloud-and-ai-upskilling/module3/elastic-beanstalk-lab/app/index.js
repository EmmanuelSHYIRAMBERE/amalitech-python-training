const express = require("express");
const {
  DynamoDBClient,
  PutItemCommand,
  ScanCommand,
} = require("@aws-sdk/client-dynamodb");

const app = express();
const port = process.env.PORT || 8080;
const TABLE_NAME = process.env.DYNAMODB_TABLE || "eb-lab-visits";
const REGION = process.env.AWS_REGION || "eu-north-1";
const APP_VERSION = process.env.APP_VERSION || "2.0.0";

const dynamo = new DynamoDBClient({ region: REGION });

async function recordVisit() {
  await dynamo.send(
    new PutItemCommand({
      TableName: TABLE_NAME,
      Item: {
        visitId: {
          S: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        },
        timestamp: { S: new Date().toISOString() },
        version: { S: APP_VERSION },
      },
    }),
  );
}

async function getVisitCount() {
  const result = await dynamo.send(
    new ScanCommand({ TableName: TABLE_NAME, Select: "COUNT" }),
  );
  return result.Count ?? 0;
}

app.get("/", async (req, res) => {
  try {
    await recordVisit();
    const count = await getVisitCount();
    res.send(`
      <!DOCTYPE html>
      <html>
        <head><title>EB Lab — Emmanuel</title></head>
        <body style="font-family:sans-serif;max-width:600px;margin:60px auto;padding:0 20px">
          <h1>🚀 Elastic Beanstalk Lab Review to the lab</h1>
          <p><strong>Version:</strong> ${APP_VERSION}</p>
          <p><strong>Total visits (DynamoDB):</strong> ${count}</p>
          <p><strong>Deployed by:</strong> Emmanuel SHYIRAMBERE</p>
          <p><strong>Time:</strong> ${new Date().toISOString()}</p>
        </body>
      </html>
    `);
  } catch (err) {
    res.status(500).send(`Error: ${err.message}`);
  }
});

app.get("/health", (req, res) =>
  res.json({ status: "ok", version: APP_VERSION }),
);

app.listen(port, () => console.log(`Server running on port ${port}`));
