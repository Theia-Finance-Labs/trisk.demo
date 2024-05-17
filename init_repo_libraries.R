# YOU NEED TO UNZIP THIS PROJECT BEFORE DOING ANYTHING
# UNZIP PROJECT, THEN DOUBLE CLICK ON  access_bank_trisk.Rproj TO OPEN RSTUDIO

# *****************************************************************************

# This script helps installing required packages to run trisk_analysis.Rmd
# Choose an option and run it line by line in the console. 
# One of the installing options should work

# ======================== OPTION 1 // Using renv

install.packages("renv")

renv::init() 

# A prompt will appear in the console. 
# Choose the following: "3: Activate the project without snapshotting or installing any packages."

renv::update()

# Wait several minutes for the update to complete
# Each time you see "Do you want to proceed? [Y/n]: ", type "Y" in the console and press Enter.

renv::restore(clean=TRUE)

# Each time you see "Do you want to proceed? [Y/n]: ", type "Y" in the console and press Enter.

# ==> You can now try to run trisk_analysis.Rmd

# use this to save your current package configuration
# and skip thos install steps next time you open this project in Rstudio
renv::snapshot() 



# ========================= OPTION 2 // install the stress test from github

# 1. Manual install by dowloading and installing the package from the source repository : 
#     https://github.com/2DegreesInvesting/trisk.model 

# 2. Automatic install in R

install.packages("remotes")
remotes::install_github("2DegreesInvesting/trisk.model")
install.packages("dplyr")

# ==> You can now try to run trisk_analysis.Rmd