# Trend Micro Vision One - File Security SDK Demo

This repository provides a **Flask-based web application** that allows users to **upload files** and scan them for malware using the **Trend Micro Vision One File Security SDK**.

---

## **1️⃣ Prerequisites**
Before setting up this demo, ensure you have:
- ✅ **Linux Machine (Ubuntu/Debian/Amazon Linux)**
- ✅ **Python 3.7+ Installed**
- ✅ **Trend Micro Vision One API Key** (With "Run file scan via SDK" permission)
- ✅ **Port 80 Open** (For web access)

---

## **2️⃣ Setup Instructions**

### **Step 1: Clone This Repository**
```bash
git clone https://github.com/your-username/repo-name.git
cd repo-name
```

### **Step 2: Install Required Dependencies**
Run the following command to install all necessary Python libraries:
```bash
pip install -r requirements.txt
```

### **Step 3: Set Environment Variables**
Replace `your-api-key` with your actual API key:
```bash
export VISION_ONE_API_KEY="your-api-key"
export VISION_ONE_REGION="us-east-1"  # Change based on your region
```

### **Step 4: Run the Flask Application**
Run the application with:
```bash
sudo -E python3 app.py
```

### **Step 5: Access the Web App**
Open your browser and go to:
```bash
http://<YOUR-PUBLIC-IP>
```
Upload a file and check if the scan works.
