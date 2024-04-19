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

    In case the analysis focuses on a single country


3. Outputs aggregation
   
   Different ways to aggregate the outputs for further analysis

   
## About Theia Finance Labs
We align financial markets with climate goals
Theia Finance Labs (Theia) acts as an incubator for and investor in public, mission driven         programmes at the intersection of finance and climate risks. TFL provides governance, as well      as strategic and operational support designed to help these projects and brands scale and          achieve long-term impact. Theia is 100% non-commercial and mission-driven.

Find out more on https://theiafinance.org

1in1000

The 1in1000 program helps financial institutions and supervisors address future risks and challenges, especially those related to climate change. The program aims to integrate risks posed by climate change, ecosystem service and biodiversity loss, and the breakdown of social cohesion into financial processes and regulations. It focuses on developing long-term risk metrics, designing risk management tools and frameworks, and building capacity for financial institutions and supervisors. Find out more at www.1in1000.com.

## Our values

Non-commercial & committed to the public good

We have no commercial contracts and provide all of our research open source and IP rights-free. This policy minimizes financial conflicts of interest and guarantees the public good-driven nature of our work.

Independent and interest-neutral

Our governance and our funding structure is designed to be diversified and multi-stakeholder. This helps ensure that our research does not represent a particular interest group, but rather our best understanding of the truth.

Science- and evidence-based

We continuously aim to expand and improve the evidence base for decision-making in sustainable finance.

## Funding

EU LIFE Project Grant

Scientific Transition Risk Exercises for Stress tests & Scenario Analysis has received funding from the European Union’s Life programme under Grant No. LIFE21-GIC-DE-Stress under the LIFE-2021-SAP-CLIMA funding call.

![](images/LifeLogo2.jpg)
