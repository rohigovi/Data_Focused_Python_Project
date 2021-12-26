import os
from datetime import date
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
import time
from Job import Job
from ZipRecruiter import ZipRecruiter
from IndeedScraper import IndeedScraper
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
headers = {'Content-Type': 'application/json'}



def apidata_Remotive(role): #optimised for 20 results to be fetched
    url = "https://remotive.io/api/remote-jobs?category="+role.replace(' ','-')
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200: 
        data = json.loads(response.content.decode('utf-8'))
        print(data['jobs'][0])
        print(type(data))
        df1 = pd.json_normalize(data['jobs'])
    
    jobs1 = df1[['title','company_name','candidate_required_location','publication_date']]
    desc= df1['description']
    desc_list = []
    for i in desc:
        desc_list.append(BeautifulSoup(i).get_text())
    jobs1['description'] =  desc_list
    jobs1['publication_date'] =  jobs1['publication_date'].str[:10]

   
    jobs1 = jobs1.rename(columns={'title': 'job_title', 'company_name': 'company_name','candidate_required_location': 'company_location', 'description': 'job_description','publication_date': 'date_posted'})    
 #   jobs2 = jobs2.rename(columns={'title': 'job_title', 'company_name': 'company_name','location': 'company_location', 'description': 'job_description'})    
    jobs_csv = jobs1.head(104)
    jobs_csv = jobs_csv[['job_title','company_name','company_location','job_description','date_posted']]
    yest = date.today()-timedelta(days=1)
    #jobsDF = jobs1.append(jobs2)
   # jobsDF.reset_index(drop=True, inplace=True)
    recent_jobs = jobs1[jobs1['date_posted']==str(yest)]
    jobs_csv.to_csv('file_name.csv', mode = 'a', sep=',')    
    jobs = jobs1.head(20)
    

    jobList = []
    for ind in jobs.index:
        job = Job(jobs['job_title'][ind], jobs['company_name'][ind], jobs['company_location'][ind], jobs['job_description'][ind],jobs['date_posted'][ind])
        jobList.append(job)
            
    for job in jobList:
        print(job.__str__())
        print('****************************************************************************')
    
    return jobs_csv
def apidata_google(role, location): #optimised for 20 results to be fetched
    url = 'https://serpapi.com/search.json?engine=google_jobs&q=' + role + location + '&hl=en&api_key=2606e41895b5d1a39ab40778b4f0050ea268e1eb5ea6a86e16595d4ad438eed9&start=0&num=10'
    response = requests.get(url, headers = headers)
    if response.status_code == 200: 
        data = json.loads(response.content.decode('utf-8'))
        df1 = pd.json_normalize(data['jobs_results'])
    url2 = 'https://serpapi.com/search.json?engine=google_jobs&q=' + role + location + '&num=20&start=20&hl=en&api_key=2606e41895b5d1a39ab40778b4f0050ea268e1eb5ea6a86e16595d4ad438eed9&start=0&num=10'
    response = requests.get(url2, headers = headers)
    if response.status_code == 200:
        data2 = json.loads(response.content.decode('utf-8'))
        df2 = pd.json_normalize(data2['jobs_results'])


    
    jobs1 = df1[['title','company_name','location','description']]
    jobs2 = df2[['title','company_name','location','description']]
    jobs1 = jobs1.rename(columns={'title': 'job_title', 'company_name': 'company_name','location': 'company_location', 'description': 'job_description'})    
    jobs2 = jobs2.rename(columns={'title': 'job_title', 'company_name': 'company_name','location': 'company_location', 'description': 'job_description'})    


    jobsDF = jobs1.append(jobs2)
    jobsDF.reset_index(drop=True, inplace=True)

    jobsDF.to_csv('file_name.csv', mode = 'a' , sep=',')    
    
    

    jobList = []
    for ind in jobsDF.index:
        job = Job(jobsDF['job_title'][ind], jobsDF['company_name'][ind], jobsDF['company_location'][ind], jobsDF['job_description'][ind], '')
        jobList.append(job)
            
        for job in jobList:
            print(job.__str__())
            print('****************************************************************************')
    return jobsDF
def scrape_indeed(role, location):

    indeed = IndeedScraper(role, location)
    indeed.scrape(role, location)
    jobList = indeed.getJobList()
    jobsDF = pd.DataFrame((job.getJobTitle(), job.getCompanyName(), job.getCompanyLocation(), job.getJobDescription().strip(), job.getJobDate()) for job in jobList)
    jobsDF = jobsDF.rename(columns={0: "job_title", 1: "company_name",2: "company_location",3: "job_description",4:"date_posted"})
    jobsDF.to_csv('filename.csv', mode = 'a' , sep=',')
    for job in jobList:       
        print(job.__str__())

        print('****************************************************************************')
    return jobsDF

def scrape_zip_recruiter(role, location):
    zip_recruiter = ZipRecruiter(role, location)
    zip_recruiter.get_url()
    job_list = zip_recruiter.get_job_list()
    if len(job_list) != 0:
        jobs_DF = pd.DataFrame(
            (job.getJobTitle(), job.getCompanyName(), job.getCompanyLocation(), job.getJobDescription()) for job in
            job_list)
        jobs_DF = jobs_DF.rename(
            columns={0: "job_title", 1: "company_name", 2: "company_location", 3: "job_description"})
        jobs_DF.to_csv('ZipRcruiter', mode='a', sep=',')
        for job in job_list:
            print(job.__str__())
            print('****************************************************************************')
    else:
        print("Sorry! No jobs found. Try another combination :).")
    
def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d}'.format(v=val)
    return my_format
    

def main():   
    while(True):
        choice = int(input("""
1: See Jobs from Serpapi (GOOGLE JOBS API). 
2: See Jobs from  Remotive (Remote ONLY)  (Remotive PI). 
3: See Jobs from Indeed (Webscraping). 
4: See Jobs from ZipRecruiter (Webscraping). 
5: See All Jobs. 
6: See Industry insights
Please enter your choice: """))
        
        role = ''
        location = ''
        df_all = pd.DataFrame()
        if choice == 2 :
            role = input('Enter the role: ')
            pd.concat([df_all, apidata_Remotive(role)],axis = 1)

        elif choice == 1:
            role = input('Enter the role: ')
            location = input ('Enter the location: ')
            pd.concat([df_all, apidata_google(role,location)],axis = 1)

        elif choice == 3:
            role = input('Enter the role: ')
            location = input ('Enter the location: ')
            pd.concat([df_all, scrape_indeed(role, location)],axis = 1)
            
        elif choice == 4:
            role = input('Enter the role: ')
            location = input('Enter the location: ')
            scrape_zip_recruiter(role, location)
        elif choice == 5:
            inp = int(input(""""Do you want(enter 1 or 2)
                        1.Analytics on your previous searches
                        2.Start a fresh search"""))
            if(inp == 1):        
                if(df_all.empty):
                    print('You don\'t have data stored from previous searches, try other menu options')
                else:
                    df_all.plot(x='date_posted', y='job_title', style='o')

                    #Plots
                
            elif(inp == 2):
                df_all_new = pd.DataFrame()
                role = input('Starting a new search...Enter the role: ')
                #Clearing the file: 
                frames = [  scrape_indeed(role,''), apidata_google(role,'')]
                df_all_new = pd.concat(frames)
                print(df_all_new)
                df_groupby =df_all_new.groupby('company_name').count().reset_index()
                df_plot = df_groupby.sort_values(['job_title'], ascending = False).head(10)
                
                import numpy as np
                # fig = plt.figure()
                # ax = plt.axes(projection='3d')
                # zline = df_groupby['job_title']
                # xline = df_groupby['company_name']
                # yline =  df_groupby['company_location']
                # ax.plot3D(xline, yline, zline, 'gray')
                # df_all_new.plot(x='date_posted', y='job_title', style='o')
                fig = plt.figure()
                ax = fig.add_axes([0,0,1,1])
                comp = df_plot['company_name']
                job_title = df_plot['job_title']
                ax.bar(comp,job_title)
                plt.xticks(rotation = 45)

                plt.show()
                df_groupby =df_all_new.groupby('company_location').count().reset_index()
                df_plot = df_groupby.sort_values(['job_title'], ascending = False).head(10)
                fig2 = plt.figure()
                ax = fig2.add_axes([0,0,1,1])
                comp = df_plot['company_location']
                job_title = df_plot['job_title']
                ax.bar(comp,job_title)
                plt.xticks(rotation = 45)

                plt.show()
        elif choice == 6:
            state = input('Please Enter the full name of the state you are interested in:\n')
            quarter1 = pd.read_csv('data\\Quarter1_StateWide.csv')
            quarter2 = pd.read_csv('data\\Quarter2_StateWide.csv')
            
            quarter1_state = quarter1[quarter1['Area'] == (state.capitalize() + ' -- Statewide')]
            quarter2_state = quarter2[quarter2['Area'] == (state.capitalize() + ' -- Statewide')]

 
            state_total_employment = quarter1_state['January Employment'] + quarter1_state['February Employment'] + quarter1_state['March Employment']
            + quarter2_state['April Employment'] + quarter2_state['May Employment'] + quarter2_state['June Employment']
        
            state_total_employment = state_total_employment.iloc[5:]
            industry = quarter1_state['Industry'].iloc[5:]
            plt.pie(state_total_employment, labels = industry)

         #   plt.pie(state_total_employment, labels = industry, autopct = autopct_format(state_total_employment))

            plt.title('Jobs added per industry in ' + state + ' from Jan-June 2021')
            plt.show()
        elif choice > 6 or choice < 0:
            quit()

if __name__=="__main__":
    main()