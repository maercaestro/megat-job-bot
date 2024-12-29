## **Megat Job Application Bot*

![LinkedIn Bot](https://img.shields.io/badge/Automation-LinkedIn-blue) ![Python](https://img.shields.io/badge/Python-3.x-yellow.svg) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)

### **Overview**
The Megat Job Application Bot automates the process of scraping job postings, analyzing job descriptions for suitability using AI, and applying for relevant positions. It is designed to streamline job searches, ensuring efficient and accurate applications.

---

### **Features**
- **Job Scraping**: Scrapes up to 20 job postings per month from selected portal
- **AI Analysis**: Uses OpenAI GPT-4o to evaluate job suitability based on your resume.
- **Application Automation**: Automatically applies to up to 5 jobs per week.
- **Categorization**: Supports filtering by job type (e.g., Data Scientist, Process Engineer).
- **Database Integration**: Stores job data and application results in MongoDB for tracking.
- **Pause and Resume**: Automatically pauses applications once weekly or monthly limits are reached.

---

### **Flowchart**
Here is a visual representation of the bot's workflow:

```mermaid
%%{init: {'theme': 'dark', 'flowchart': {'direction': 'TB'}}}%%
flowchart TB
    A[Start] --> B[Scrape Job Postings]
    B --> C[Check Monthly Scrape Limit]
    C -->|Limit Reached?| D[Stop Scraping for This Month]
    C -->|Not Reached| E[Determine Job Type]
    
    E --> F[Data Scientist Jobs]
    E --> G[Process Engineer Jobs]
    F --> H[Send Job Description to AI Agent]
    G --> H

    H --> I[Analyze Suitability with Resume Summary]
    I --> J[Store Analysis and Job Info in Database]
    J --> K[Applier Bot Pulls Data]
    
    K --> L[Check Weekly Application Limit]
    L -->|Limit Reached?| M[Pause Applications for This Week]
    L -->|Not Reached| N[Apply for Jobs]

    M --> O[Wait Until Next Week]
    N --> L
    O --> K
    D --> P[Wait Until Next Month]
    P --> B
```

---

### **Technologies Used**
- **Programming Language**: Python
- **Libraries**:
  - Selenium: For web scraping and automation.
  - Beautiful Soup: For parsing job descriptions.
  - OpenAI: For AI-based job analysis.
  - MongoDB: For storing job and application data.
  - Python `dotenv`: For securely managing environment variables.
- **Hosting**: Azure VM (Ubuntu 22.04).

---

### **Setup Instructions**

#### **1. Clone the Repository**
```bash
git clone https://github.com/maercaesgtro/megat-job-bot.git
cd megat-job-bot
```



#### **3. Set Up Environment Variables**
Create a `.env` file in the root directory and add your credentials:
```plaintext
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/myFirstDatabase
OPENAI_API_KEY=your-openai-api-key
```

#### **4. Configure Job Search Filters**
Modify `config.py` to specify job search preferences:
```python
keywords = ["data scientist", "process engineer"]
location = ["North America"]
datePosted = ["Past Week"]
jobType = ["Full-time"]
```


---

### **Usage Notes**
1. **Limits**:
   - The bot scrapes **20 job postings per month** and applies to **5 jobs per week**.
2. **Database**:
   - MongoDB stores job postings, analysis, and application results.

---

### **Project Structure**
```
.
├── linkedin.py          # bot script for Linkedin
├── scraper.py           # bot script for scraping specific portal
├── scraper2.py          # bot script for applying the selected job
├── config.py            # Job search filters and configuration            
└── README.md            # Project documentation
```

---

### **Future Enhancements**
- Add more AI-based analysis for job descriptions.
- Extend support for other job boards like Indeed and Glassdoor.
- Implement a dashboard for visualizing application statistics.

---

### **Contributing**
Contributions are welcome! Please open an issue or submit a pull request.

---

### **License**
This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

### **Contact**
For any questions or suggestions, feel free to contact:
- **Name**: Abu Huzaifah Bidin
- **Email**: maercaestro@gmail.com


