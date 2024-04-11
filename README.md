# trisk.demo
Library of example scripts to generate and analyse trisk simulations.

Explore the underlying model source code : https://github.com/2DegreesInvesting/r2dii.climate.stress.test
Pre-configured plots to use for exploration or presentation of trisk results : https://github.com/2DegreesInvesting/stress.test.plot.report/tree/master 

# User guide

## Set up

1. Install packages
- On this page, click on the green button "Code", then on "Download ZIP", to download this project as “trisk.demo.zip”
- Unzip the folder to your PC
- Open the unzipped folder, and double click on access_bank_trisk.Rproj This will open an R studio Session
- In the “Files” tab in R studio where you can see the entire project structure, click on `init_repo_librairies.R` to open it in the editor tab.
- Here you find two different options to run the stress test. For now, follow the steps highlighted by Option 1.


2. Initialize the data inputs
- When you completed the steps, go back to the "trisk.demo" folder and open the `st_input/` folder. The two files are dummy files that you want to replace. Please just replace the files with the datafiles you have available for abcd_stress_test_input.csv and prewrangled_financial_data_stress_test.csv
- Now navigate back to the Rstudio session you opened. Under files, you can see `init_repo_data.Rmd` . Click this to open it.
- Navigate to the top of Rstudio and press Run, then in the dropdown menu that opens, press Run All
- You can find the output results then in the `st_outputs/` folder in the "trisk.demo" folder
- If you want to change the settings of the stress test you can follow the script `init_repo_data.Rmd` to see available parameter settings. In line 75 to 85 you can then change the settings. After changing the settings just press Run All again to extract the outputs in the ST_Output folder


## Available analysis

In the `scripts/` folder, you will find different examples on how to run trisk

1. Multi-run

    Source `trisk_multirun.R` to loop over multiple run parameters, each new run defined with a new list() element. Undefined parameters will be the defaults of trisk.


2. Country specific dataprep

    In case th analysis focuses on a single country


3. Outputs aggregation
   
   Different ways to aggregate the outputs for further analysis