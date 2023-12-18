import os
import pandas as pd
from jinja2 import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import zipfile
import sys


class GenerateReports:

    def __time_to_seconds(self, time_str):
        parts = time_str.split()
        minutes = 0
        seconds = 0
        for part in parts:
            if 'm' in part:
                minutes += float(part.strip('m'))
            elif 's' in part:
                seconds += float(part.strip('s'))
        total_seconds = minutes * 60 + seconds
        return total_seconds


    def __convert_time_to_seconds(self, time_str):
        minutes, seconds = 0, 0
        parts = time_str.split()
        for part in parts:
            if 'm' in part:
                minutes = int(part.replace('m', ''))
            elif 's' in part:
                seconds = float(part.replace('s', ''))
        return (minutes * 60) + seconds


    def __find_max_time_duration(self, time_list):
        max_duration = 0
        for time_str in time_list:
            duration_in_seconds = self.__convert_time_to_seconds(time_str)
            max_duration = max(max_duration, duration_in_seconds)
        return max_duration


    def generate_report_by_combining_different_reports(self, number_of_collections, collection_name):

        try :

            # Fetching current working directory
            current_directory = os.getcwd()

            # Converting number_of_collections from string to int
            number_of_collections = int(number_of_collections)

            # Declaring variables and lists for appropriate attributes related to collections
            primary_req_list_sum = 0    # Sum of request attributes
            secondary_req_list_sum = 0   # Another variable for request attributes

            primary_pre_req_digit = 0   # Sum of pre-request script attributes
            secondary_pre_req_digit = 0  # Another variable for pre-request script attributes

            primary_test_scripts_digit = 0  # Sum of test script attributes
            secondary_test_scripts_digit = 0  # Another variable for test script attributes

            primary_asser_digit = 0   # Sum of assertion attributes
            secondary_asser_digit = 0  # Another variable for assertion attributes

            total_run_duration_list = []
            html_files_for_attachment = []
            counter_variable = 1
            combined_contents = ""

            # Using for loop to get input file as a html from local system
            for i in range(1, number_of_collections + 1):

                html_template = {
                    "path" : "",
                    "url": ""
                }

                # Specify the file path
                generated_html_file_path = f'{current_directory}/source/.tmp/reports/html/{collection_name}-group-{i}.postman_collection.html'

                # Open the file in read mode ('r')
                with open(generated_html_file_path , 'r') as file:
                    # Read the entire contents of the file
                    generated_html_file_contents = file.read()

                # Creating empty list to store my html elemnts to list elements
                htmlFileToList = []

                # Using the for loop split my html code line by line
                for line in generated_html_file_contents.split("\n"):
                        htmlFileToList.append(line)

                timeStamp = [htmlFileToList[30], htmlFileToList[42]]
                time = htmlFileToList[30].split('<div class="col-md-3">Time</div><div class="col-md-9">')
                total_run_duration = htmlFileToList[42].split('<div class="col-md-6">Total run duration</div><div class="col-md-6">')
                time_in_str = time[1].replace('</div>',"")
                total_run_duration_in_str = total_run_duration[1].replace("</div>","")
                total_run_duration_list.append(total_run_duration_in_str)


                # Convert all time strings to seconds and calculate the average
                total_seconds = sum( self.__time_to_seconds(time_str) for time_str in total_run_duration_list)
                average_seconds = total_seconds / len(total_run_duration_list)

                # Round the average to two decimal places
                average_time = round(average_seconds, 2)

                # Convert average back to a readable time format
                average_minutes = int(average_time // 60)
                average_seconds = average_time % 60
                total_run_duration_in_str = f"{average_minutes}m {average_seconds:.2f}s"

                # total_run_duration_list = ['6m 13.9s', '6m 32.8s', '9m 38.3s', '10m', '6m 36.2s', '9m 28.6s', '5m 43.4s', '9m 8.2s', '10m 36.6s', '11m 53.4s', '6m 5.2s', '9m 29.7s', '57.8s', '2m 54.1s', '6m 57.6s', '4m 53.2s', '4m 40s', '2m 45.6s', '5m 6.6s', '5m 7.5s', '7m 11.2s', '3m 2.6s', '41s', '5m 19.3s', '7m 27.4s', '7m 34.3s']

                max_duration_in_seconds = self.__find_max_time_duration(total_run_duration_list)
                max_time_from_all_groups = (f"{int(max_duration_in_seconds // 60)}m {max_duration_in_seconds % 60:.1f}s")
                max_with_int_plus_by_one = int(max_time_from_all_groups.split('m')[0]) + 1.5


                div_tag_of_time_in_str = list(f'        <div class="col-md-3">Time</div><div class="col-md-9">{time_in_str}</div>')
                div_tag_of_total_run_in_str = list('        <div class="col-md-6">Total run duration</div><div class="col-md-6">{total_run_duration_in_str}/div>')


                # Searching our useful table from entire html code and finding the start and end position of our table
                startPositionOfTable = (htmlFileToList.index("    <h3>Newman Report</h3>"))
                endPositionOfTable = (htmlFileToList.index('    <br/><h4>Requests</h4>'))

                list_with_startAndEnd_table = []

                for i in range (startPositionOfTable + 1, endPositionOfTable):
                    list_with_startAndEnd_table.append(htmlFileToList[i])

                list_with_eachline_withpop_of_div_elemnet=[]
                list_with_splitof_eachline_without_suffixof_div=[]

                # final_usefull_attr is the list which has all soretd (start to end useful table) elemnets in list, it has line soretd elemnets
                final_usefull_attr=list_with_startAndEnd_table[9:13]

                # Using for loop to get in to each and every line which has stored in final_usefull_attr list
                for i in final_usefull_attr:
                    # Storing each line in one temporary string
                    tmpr_string=str(i)

                    # spliting our line inside the list when by "</"
                    list_with_eachline_withpop_of_div_elemnet = list(tmpr_string.split("</"))

                    # End of the each and every line has "</div>" tag which is not usefull to make some oparation are easy we are poping it from each and every line
                    list_with_eachline_withpop_of_div_elemnet.pop()

                    # Using one more for loop inside the for loop to append each element of each line with each list in side the list_with_splitof_eachline_without_suffixof_div
                    for j in list_with_eachline_withpop_of_div_elemnet:
                        list_with_splitof_eachline_without_suffixof_div.append(j)

                list_with_useful_digits_and_oparations_name=[]
                # Getting each sub line from one single line by using for loop
                for i in list_with_splitof_eachline_without_suffixof_div:
                    # Storing each subline in temp variable
                    i=str(i)

                    # spliting those lines from "<div class=\"col-md-4\">" because that one is not useful and again converting remaing words or line or degit in to list
                    # 1. split it from "<div class=\"col-md-4\">"
                    # 2. split it from with or condition "div<div class=\"col-md-4\">"
                    # 3. remaning string convert in to list
                    # 4. Using one  temporary list to make our sorting easy
                    tempConvertStringToList=(list(i.split("<div class=\"col-md-4\">"))) or (list(i.split("div><div class=\"col-md-4\">")))
                    list_with_useful_digits_and_oparations_name.append(tempConvertStringToList)


                # Using for loop to travell in list_with_useful_digits_and_oparations_name's elements
                for i in list_with_useful_digits_and_oparations_name:
                    # Deleting first element of each list that is not usefull by pop(0)
                    i.pop(0)
                list_whichhas_oparation_passCases_failedCases=[]
                for i in list_with_useful_digits_and_oparations_name:
                    list_whichhas_oparation_passCases_failedCases.append(i[0])


                # Assuming the empty list before start any itreation
                # 4 Lists with name of Result

                Request_list=[]
                Pre_Scripts=[]
                Test_Scripts=[]
                Assertions=[]


                # For loop to set appropiate entity in to appropiate list so use can use it easily
                for i in range (0,len(list_whichhas_oparation_passCases_failedCases)):
                    if i<=2:
                        Request_list.append(list_whichhas_oparation_passCases_failedCases[i])
                    if i>=3 and i<=5:
                        Pre_Scripts.append(list_whichhas_oparation_passCases_failedCases[i])
                    if i>=6 and i<=8:
                        Test_Scripts.append(list_whichhas_oparation_passCases_failedCases[i])
                    if i>=9:
                        Assertions.append(list_whichhas_oparation_passCases_failedCases[i])

                # Using the for loop to sum of all my attributes of respective lists
                for i in range(1,3):
                    if i==1:
                        primary_req_list_sum+=int(Request_list[i])
                        primary_pre_req_digit+=int(Pre_Scripts[i])
                        primary_test_scripts_digit+=int(Test_Scripts[i])
                        primary_asser_digit+=int(Assertions[i])
                    if i==2:
                        secondary_req_list_sum+=int(Request_list[i])
                        secondary_pre_req_digit+=int(Pre_Scripts[i])
                        secondary_test_scripts_digit+=int(Test_Scripts[i])
                        secondary_asser_digit+=int(Assertions[i])
                html_files_for_attachment.append(f"{current_directory}/source/.tmp/reports/html/{collection_name}-group-{counter_variable}.postman_collection.html" )
                counter_variable+=1

            # Logic for get all csv file and consodiate all csv file in to one single file
            for i in range(1,number_of_collections+1):
                if i==1:
                    file_path_of_1st_csv_file = f'{current_directory}/source/.tmp/reports/csv/{collection_name}-group-{i}.postman_collection.csv'
                    with open(file_path_of_1st_csv_file, 'r') as file:
                        file_contents = ''.join(file.readlines()[0:])
                    combined_contents = file_contents
                else:
                    file_path_whichis_opening_csv_report_which_is_generatedby_newman = f'{current_directory}/source/.tmp/reports/csv/{collection_name}-group-{i}.postman_collection.csv'

                    # Open and read the second file (file_path1) without the header
                    with open(file_path_whichis_opening_csv_report_which_is_generatedby_newman, 'r') as file1:
                        # Skip the first line (header) using readlines()[1:]
                        file_contents1 = ''.join(file1.readlines()[1:])

                    # Combine the contents of the two files
                    combined_contents += "\n"+ file_contents1
            # Specify the path where you want to save the CSV file
            csv_file_path_to_save_consodilated_outputs_csvs =  f'{current_directory}/source/report.csv'  # Change to your desired file path

            with open(csv_file_path_to_save_consodilated_outputs_csvs, 'w') as file:
                # Write the output content to the file
                file.write(combined_contents)

            # print(f'Consodileted csv file has been saved to {csv_file_path_to_save_consodilated_outputs_csvs}')
            # print(csv_file_path_to_save_consodilated_outputs_csvs)
            # Final list which has all attributes
            list_with_all_attr=[['Requests',str(primary_req_list_sum),str(secondary_req_list_sum)],['Prerequest Scripts',str(primary_pre_req_digit),str(secondary_pre_req_digit)],['Test Scripts',str(primary_test_scripts_digit),str(secondary_test_scripts_digit)],['Assertions',str(primary_asser_digit),str(secondary_asser_digit)]]

            list_whichhas_oparation_passCases_failedCases=list_with_all_attr

            # Op 2: Taking sample file and pushing our normalized data into this file
            # Sample file oparations
            # Get uril of sample template or sample file and give it here
            # url = f"{current_directory}/source/.tmp/template/tmplt.html"

            # read_htmlFile=pd.io.html.read_html(url)
            # read_htmlFile=pd.read_fwf(url)

            # Specify the file path
            template_file_path = f'{current_directory}/source/.tmp/resources/template.html'
            # Open the file in read mode ('r')
            with open(template_file_path, 'r') as file:
                # Read the entire contents of the file
                file_contents = file.read()


            # temporary lists of appropiate results just for
            temporary_list_of_requests=[]
            temporary_list1_of_requests=[]
            temporary_list_of_prerequestScripts=[]
            temporary_list1_of_prerequestScripts=[]
            temporary_list_of_testScripts=[]
            temporary_list1_of_testScripts=[]
            temporary_list1_of_assertions=[]
            temporary_list_of_assertions=[]

            # prefix tags of html code that we can use in loop mode
            prefix_of_htmltag=['<td class="text-center">']
            prefix1_of_htmltag=['</td>']
            prefix2_of_htmltag=['<td id="m_4984826125979941932v2-percentage">']
            prefix3_of_htmltag=[' </td>']


            # Total and failed Assertions
            total_asserations=[]
            failed_assertions=[]


            finalized_html_list=[]

            list_with_splitingby_eachline_from_sampleHtml=[]

            # spliting  each line in to list_with_splitingby_eachline_from_sampleHtml list
            for line in file_contents.split("\n"):
                list_with_splitingby_eachline_from_sampleHtml.append(line)

            list_with_splitingby_eachline_from_sampleHtml[56]=time_in_str

            position_set_of_time=f'            <td id="m_4984826125979941932total-run-duration"> {total_run_duration_in_str} </td>'
            list_with_splitingby_eachline_from_sampleHtml[72]=position_set_of_time

            set_index_of_name='            <td id="m_4984826125979941932date"> FX-Nightly Build</td>'
            list_with_splitingby_eachline_from_sampleHtml[61]=set_index_of_name

            set_index_of_timer='            <td id="m_4984826125979941932started-by"> Newman </td>'
            list_with_splitingby_eachline_from_sampleHtml[51]=set_index_of_timer


            for i in range(0,len(list_with_splitingby_eachline_from_sampleHtml)):

                # loop will run while my i <len(givenlist) because here i am reduceing line so
                if i<len(list_with_splitingby_eachline_from_sampleHtml):

                    # if Given html tag is '            <td style="width: 20%">Pass %</td>'  then we have to return passing percentage_assertion
                    if list_with_splitingby_eachline_from_sampleHtml[i]=='            <td style="width: 20%">Pass %</td>':
                        total_asserations=list_whichhas_oparation_passCases_failedCases[3][1]
                        failed_assertions=list_whichhas_oparation_passCases_failedCases[3][2]
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i+1])

                        if failed_assertions[0]=="0":
                            percentage_assertion="100"
                        else:
                            failedAssertionswith100=str(((100*int(failed_assertions[0]))))
                            total_assetaionsin_str=str(total_asserations)
                            total_failed_percentage=(int(failedAssertionswith100)/int(total_assetaionsin_str))
                            total_passed_percentage_in_string=float(100.00-(total_failed_percentage))
                            rounding_off=round(total_passed_percentage_in_string,2)
                            percentage_assertion=(str(rounding_off))

                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i+1])
                        finalized_html_list.append("            <td style=\"width: 20%\">Pass %</td>")
                        finalized_html_list.append(' '.join(prefix2_of_htmltag+list(percentage_assertion)+prefix3_of_htmltag))

                    # Checking and updating for Requests
                    elif list_with_splitingby_eachline_from_sampleHtml[i] =='            <td>Requests</td>':
                        temporary_list_of_requests.append((list_with_splitingby_eachline_from_sampleHtml[i+1]).split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list1_of_requests.append(list_with_splitingby_eachline_from_sampleHtml[i+2].split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list_of_requests[0]=list_whichhas_oparation_passCases_failedCases[0][1]
                        temporary_list1_of_requests[0]=list_whichhas_oparation_passCases_failedCases[0][2]
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i])
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i+1])
                        finalized_html_list.append("<td>Requests</td>")
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list_of_requests+prefix1_of_htmltag))
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list1_of_requests+prefix1_of_htmltag))

                    # Checking and updating for rerequest Scripts
                    elif list_with_splitingby_eachline_from_sampleHtml[i] =='            <td>Prerequest Scripts</td>':
                        temporary_list_of_prerequestScripts.append((list_with_splitingby_eachline_from_sampleHtml[i+1]).split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list1_of_prerequestScripts.append(list_with_splitingby_eachline_from_sampleHtml[i+2].split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list_of_prerequestScripts[0]=list_whichhas_oparation_passCases_failedCases[1][1]
                        temporary_list1_of_prerequestScripts[0]=list_whichhas_oparation_passCases_failedCases[1][2]
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i])
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i+1])
                        finalized_html_list.append('<td>Prerequest Scripts</td>')
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list_of_prerequestScripts+prefix1_of_htmltag))
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list1_of_prerequestScripts+prefix1_of_htmltag))

                        # Checking and updating for Test Scripts
                    elif list_with_splitingby_eachline_from_sampleHtml[i] =='            <td>Test Scripts</td>':
                        temporary_list_of_testScripts.append((list_with_splitingby_eachline_from_sampleHtml[i+1]).split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list1_of_testScripts.append(list_with_splitingby_eachline_from_sampleHtml[i+2].split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list_of_testScripts[0]=(list_whichhas_oparation_passCases_failedCases[2][1])
                        temporary_list1_of_testScripts[0]=(list_whichhas_oparation_passCases_failedCases[2][2])
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i])
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i+1])
                        finalized_html_list.append('<td>Test Scripts</td>')
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list_of_testScripts+prefix1_of_htmltag))
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list1_of_testScripts+prefix1_of_htmltag))

                    # Checking and updating for Asserations
                    elif list_with_splitingby_eachline_from_sampleHtml[i] =='            <td>Assertions</td>':
                        temporary_list1_of_assertions.append((list_with_splitingby_eachline_from_sampleHtml[i+1]).split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list_of_assertions.append(list_with_splitingby_eachline_from_sampleHtml[i+2].split("<td class=\"text-center\">").pop(1).replace("</td>",""))
                        temporary_list1_of_assertions[0]=list_whichhas_oparation_passCases_failedCases[3][1]
                        temporary_list_of_assertions[0]=list_whichhas_oparation_passCases_failedCases[3][2]
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i])
                        list_with_splitingby_eachline_from_sampleHtml.remove(list_with_splitingby_eachline_from_sampleHtml[i+1])
                        finalized_html_list.append('<td>Assertions</td>')
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list1_of_assertions+prefix1_of_htmltag))
                        finalized_html_list.append(' '.join(prefix_of_htmltag+temporary_list_of_assertions+prefix1_of_htmltag))

                    else:
                        finalized_html_list.append(list_with_splitingby_eachline_from_sampleHtml[i])

            # x=x+x2+x3
            # finalized_html_list.insert(-3,x)
            final_string=" ".join(finalized_html_list)
            # print(final_string)


            # Merging all HTML reports and attaching via mail
            # Initialize an empty string to store the combined HTML content
            combined_html = ''

            # Read the contents of each HTML file and append it to the combined_html string
            for file_path in html_files_for_attachment:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    combined_html += file_content

            # Specify the path for the output merged HTML file
            output_file_path_of_attachment = f"{current_directory}/source/report.html"

            # Write the combined HTML content to the output file
            with open(output_file_path_of_attachment, 'w', encoding='utf-8') as output_file:
                output_file.write(combined_html)


            html_file_path = f'{current_directory}/source/.tmp/output.html'

            # Open the file in write mode and write the HTML string to it
            with open(html_file_path, 'w') as html_file:
                html_file.write(final_string)


            # Creating CSV to HTML report
            csv_file_path_of_merged_cvs = f'{current_directory}/source/report.csv'
            html_output_file_of_merged_csv_to_html = f'{current_directory}/source/consolidated.html'

            # Read the CSV file using pandas
            df = pd.read_csv(csv_file_path_of_merged_cvs)

            # Remove the second column (assuming it's indexed as 1, Python uses 0-based indexing)
            df = df.drop(df.columns[1], axis=1)

            # Customize the HTML template
            template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th, td {
                        border: 1px solid #dddddd;
                        text-align: left;
                        padding: 8px;
                    }
                    tr:nth-child(even) {
                        background-color: #f2f2f2;
                    }
                    th {
                        background-color: #4CAF50;
                        color: white;
                    }
                </style>
            </head>
            <body>
                <h2>Consolidated HTML Report</h2>
                <table>
                    <tr>
                        {% for col in columns %}
                        <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                    {% for index, row in data.iterrows() %}
                    <tr>
                        <td>{{ index + 1 }}</td>
                        {% for col in columns %}
                        <td>{{ row[col] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </table>
            </body>
            </html>
            """

            # Create a Jinja2 template from the customized HTML template
            html_template = Template(template)

            # Render the HTML template
            rendered_html = html_template.render(columns=df.columns, data=df)

            # Save the HTML report to a file
            with open(html_output_file_of_merged_csv_to_html, 'w', encoding='utf-8') as html_file:
                html_file.write(rendered_html)

            filepath_of_merged_csv_for_segregation = f'{current_directory}/source/report.csv'

            # Load the CSV file into a pandas DataFrame
            df = pd.read_csv(filepath_of_merged_csv_for_segregation)

            # Define the column name to search in
            column_name = 'requestName'

            # Convert the column values and search strings to lowercase for case-insensitive search
            df[column_name] = df[column_name].str.lower()
            search_strings = ['ingest a gross cashflow', 'ingest the netted cashflow', 'get the status of settled gross cashflow', 'get the status of settled netted cashflow']

            # Count occurrences of specific strings in the 'requestName' column (case-insensitive)
            count_results = [df[column_name].str.count(search_string).sum() for search_string in search_strings]

            # Print the counts of each string found in the 'requestName' column
            gross=count_results[0]
            netted=count_results[1]
            settled_gross=count_results[2]
            settled_netted=count_results[3]
            settled=settled_netted+settled_gross
            # Get the current working directory

            # Define the file path for the HTML file
            html_file_path = f'{current_directory}/source/.tmp/output.html'

            # Initialize the string variable
            segregation_digits = ""

            # Read the content of the HTML file and store it in the variable
            with open(html_file_path, 'r', encoding='utf-8') as html_file:
                segregation_digits = html_file.read()

            # Now, 'segregation_digits' contains the content of the HTML file as a string
            segregation_digits=segregation_digits.replace(f'digit1',f'{gross}')
            segregation_digits=segregation_digits.replace('digit2',f'{netted}')
            segregation_digits=segregation_digits.replace('digit3',f'{settled}')

            # Define the file path for the output HTML file (same location as the original HTML file)
            output_html_file_path_of_after_segregation_digits = f'{current_directory}/source/.tmp/output.html'

            # Write the modified content to the output HTML file
            with open(output_html_file_path_of_after_segregation_digits, 'w', encoding='utf-8') as output_html_file:
                output_html_file.write(segregation_digits)

            return output_file_path_of_attachment
        except:
            raise Exception("Sorry! Something went wrong")

generate_reports_object = GenerateReports()
collection_name, size = sys.argv[1:3]
generate_reports_object.generate_report_by_combining_different_reports(size, collection_name)