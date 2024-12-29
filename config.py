# config.py

# Browser Settings
browser = ["Chrome"]          # Use Chrome as default
headless = False              # Set to True to run in the background

# Job Search Filters
location = ["North America"]                     # Locations for the job search
keywords = ["frontend", "react", "python"]       # Job search keywords
experienceLevels = ["Entry level"]               # Experience level
datePosted = ["Past Week"]                       # Posted within the past week
jobType = ["Full-time"]                          # Job type
remote = ["Remote", "Hybrid"]                    # Remote or hybrid jobs
salary = ["$80,000+"]                            # Salary filter
sort = ["Recent"]                                # Sort by Recent or Relevant

# Blacklist/Whitelist
blacklistCompanies = ["CompetitorCompany"]       # Skip these companies
blackListTitles = ["Intern", "Junior"]           # Skip these job titles
onlyApplyCompanies = []                          # Apply only to these companies
onlyApplyTitles = []                             # Apply only to these job titles

# Job Application Settings
followCompanies = False                          # Follow companies after applying
preferredCv = 1                                  # Use the first uploaded resume

# Debugging & Testing
displayWarnings = True                           # Show warnings in the console
