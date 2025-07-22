```mermaid
graph TD
A[Google Sheet Input Data] --> B{Trigger Automation}
B --> C[Read Data from Google Sheet]
C --> D{Loop through each row}
D --> E[Call AI Model: OpenAI / Claude]
E --> F{Generate Asset: PNG, JPG, GIF, MP3}
F --> G[Store Asset in Google Drive]
G --> H{Log Task Status to Database}
H --> I{Send Notification via Email/Slack (Success/Failure)}
I --> J{Daily Report Generation}
J --> K[Generate Analytics Chart]
K --> L[Email Summary Report to Admin]
```
