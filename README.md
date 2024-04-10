# trisk.demo
Library of scripts to generate and analyse trisk simulations


How to use : 
- On this page, click on the green button "Code", then on "Download ZIP", to download this project as “trisk.demo.zip”
- Unzip the folder to your PC
- Open the unzipped folder, and double click on access_bank_trisk.Rproj This will open an R studio Session
- In the “Files” tab in R studio where you can see the entire project structure, click on RUN_ME_FIRST.R to open it in the editor tab.
- Here you find two different options to run the stress test. For now, follow the steps highlighted by Option 1.
- When you completed the steps, go back to the “trisk_demo_project” and open the st_input folder. The two files are dummy files that you want to replace. Please just replace the files with the datafiles you have available for abcd_stress_test_input.csv and prewrangled_financial_data_stress_test.csv
- Now navigate back to the Rstudio session you opened. Under files, you can see trisk_analysis.Rmd. Click this to open it.
- Navigate to the top of Rstudio and press Run, then in the dropdown menu that opens, press Run All
- You can find the output results then in the ST_Output folder in the "trisk_demo_project" folder
- If you want to change the settings of the stress test you can follow the script trisk_analysis.Rmd to see available parameter settings. In line 75 to 85 you can then change the settings. After changing the settings just press Run All again to extract the outputs in the ST_Output folder
