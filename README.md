
# Platform Usage Tracker

Platform Usage Tracker is an application designed for easy consolidation of monthly usage reports. It allows users to upload required files and generate summarized and consolidated consumption reports effortlessly.

---

## Steps to Run

Follow these steps to set up and run the application on your local machine:

1. Open your terminal.
2. Run the following commands:

   ```bash
   git clone https://github.com/gyan-sharma/billingtracker
   cd billingtracker
   chmod +x run.sh
   ./run.sh
   ```

3. After running the commands, you will see the following message on the terminal:

   ```
   Starting backend server on port 5002...
   Starting frontend server on port 8002...
   Setup complete!
   Backend is running on: http://127.0.0.1:5002
   Frontend is running on: http://127.0.0.1:8002
   ```

4. Open your browser and navigate to:  
   [http://127.0.0.1:8002](http://127.0.0.1:8002)

5. Upload the required files (Price file and Usage files) through the frontend interface.

6. Generate and download summarized and consolidated consumption reports in a few clicks

---

## Features

- **Easy File Upload**: Drag-and-drop or select files directly in the browser.
- **Automated Processing**: Backed by a Python backend to process and consolidate your reports.
- **Downloadable Results**: Generate detailed and summary reports instantly.
- **User-Friendly Interface**: Simplified UI with clear instructions for easy operation.

---

## Repository Structure

```plaintext
billingtracker/
├── backend/
│   ├── app.py
│   ├── process.py
│   ├── uploads/
│   ├── outputs/
├── frontend/
│   ├── index.html
│   ├── settlemint_logo.png
├── run.sh
├── README.md
```

---

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Dependencies**: 
  - Flask
  - Flask-CORS
  - pandas
  - openpyxl
  - xlsxwriter

---

## License

© 2024 SettleMint. All rights reserved.
