# Assignment - Zivver

## My Soluton
*please note that i used an AI tool (github copilot) to help with debugging and writing somes notes. all instances of AI usage are clearly marked with a comment*

### Data Transformation
**Language Choice:** Python

**Libraries Used:**
*   `json` - for parsing and manipulating JSON data.
*   `os` - for file and directory operations.

**Script:** `processingData.py`

**How to Run Locally:**

1.  **Prereqs:**
    *   install python3
    *   clone the project onto local machine
    *   The sample data files (`2021-01-10.txt`, `2021-01-11.txt`) should be located in the `data/data-exports/TPCDS_SF10TCL/customer/` directory relative to the script.

2.  **Navigate to the project directory:**
    ```bash
    cd path/to/DataEngineer-assignment_2025 
    ```

3.  **Run the script:**
    ```bash
    python processingData.py 
    ```
    (Or `/opt/anaconda3/envs/bootcamp/bin/python processingData.py` if you prefer to specify the interpreter directly). same result.

4.  **Output:**
    *   transformed files will be created in a new folder called `output_data/`.
    *   each transformed file will be named with a `_transformed` suffix (e.g., `2021-01-10_transformed.txt`).
    *   json decoding errors are printed to the console and logged in `error_log.txt`.

**Script Logic Overview:**

the script (`processingData.py`) performs the following for each `.txt` file i was given:
1.  Reads each line, expecting a JSON object.
2.  Removes the `C_FIRST_NAME` and `C_LAST_NAME` fields from the JSON object.
3.  **Email Processing:**
    *   Extracts the value of `C_EMAIL_ADDRESS`
    *   Parses this value to get the domain part (everything after the "@" symbol)
    *   Stores this domain in a new field called `C_EMAIL_DOMAIN`
    *   Deletes the original `C_EMAIL_ADDRESS` field
    *   If `C_EMAIL_ADDRESS` is missing or malformed, `C_EMAIL_DOMAIN` is set to `null`
4.  writes the modified JSON object as a new line to a corresponding file in the `output_data` directory
5.  Handles empty lines and potential JSON decoding errors gracefully :)

### Loading to an OLAP System
*used AI to organize the notes and make them more structured*

### Loading Transformed Data to an OLAP System (SCD Type 2)

To load the transformed customer data into an OLAP system and keep the history of each record, I would *SCD Type 2*. 

#### 1. The main customer table (like `Dim_Customer`):

The main customer table in the warehouse would store not just the latest customer info, but all historical versions. It'd have the regular customer details from our transformed files (like `C_CUSTOMER_SK`, `C_EMAIL_DOMAIN`, `C_BIRTH_COUNTRY` etc.) and these extra columns to manage the history:

- `Customer_Dim_Key`: unique ID for every single row in this table (this is the table's primary key).
- `C_CUSTOMER_SK`: The customer's main ID from the original data. This helps us link all historical versions of the *same* customer
- `Effective_Start_Date`: The date when this particular version of the customer's information became 'current' or 'effective.'
- `Effective_End_Date`: The date when this version of the customer's information stopped being "current." For the very latest version, this would be empty or set to a far-future date like '9999-12-31' 
- `Is_Current_Flag`: A simple flag like `Y` or `N` that makes it easy to find the most up-to-date record for any customer

#### 2. The Daily Loading Process:

Every day, when we get a new transformed data file (e.g `2021-01-10_transformed.txt`) we can run this process:

**a. Stage Today's Data:**  
Load the transformed data from the daily file into a temporary "staging" table.

**b. Process Each Customer from Today's File:**

For each customer record in the staging table:

- **i. Is this a brand-new customer?**
    - Check if their `C_CUSTOMER_SK` already exists with `Is_Current_Flag = TRUE` in our main `Dim_Customer` table.
    - If not, we add them as a new row to `Dim_Customer`. Their `Effective_Start_Date` is today's date, `Effective_End_Date` is empty/far-future, and `Is_Current_Flag` is TRUE.

- **ii. Is this an existing customer? Did their info change?**
    - If they are already in `Dim_Customer` as a current record:
        - Compare their details from today's file (staging table) with their current details in `Dim_Customer`.
        - **If nothing changed:** We don't need to do anything.
        - **If something changed** (e.g., their email domain is different):
            1. **Mark the old record as "not current":** In `Dim_Customer`, find their old current record, set its `Effective_End_Date` to yesterday's date, and change `Is_Current_Flag` to FALSE.
            2. **Add the new record as "current":** Add a new row to `Dim_Customer` with their updated information. This new row gets today's date as `Effective_Start_Date`, an empty/far-future `Effective_End_Date`, and `Is_Current_Flag` set to TRUE.

**c. Handle Customers Who Are No Longer in the Daily File:**

- Since the daily export is a "full data export," if a customer was marked as current in our `Dim_Customer` table but *isn't* in today's data file, we can assume they've left or are no longer active.
- For these customers, we'd update their last current record in `Dim_Customer` by setting the `Effective_End_Date` to yesterday's date and `Is_Current_Flag` to FALSE.

#### 3. How Analysts Can Use This Historical Data:

- **To get the latest info for all customers:** Query `Dim_Customer` where `Is_Current_Flag = TRUE`.
- **To see what a customer's info looked like on a specific past date (e.g., '2021-01-15'):** Query `Dim_Customer` where the specific date is between that record's `Effective_Start_Date` and `Effective_End_Date` (or where `Effective_End_Date` is still empty if it's the current record for that date).

This SCD Type 2 approach ensures we keep a full audit trail of customer changes, which is exactly what the analysts will need for historical reporting.

---
## Sources

The sample dataset is a subset of the [TPC-DS benchmark](http://www.tpc.org/tpc_documents_current_versions/pdf/tpc-ds_v2.5.0.pdf)
available as sample data in [Snowflake](https://docs.snowflake.com/en/user-guide/sample-data-tpcds.html).


## Initial Assignment

Congratulations! This is your first day at your new job!

You start your day energized and excited about all these new learning opportunities and
awesome colleagues. After having your favourite morning beverage, you are ready to 
attend your daily meeting with your team.

During that meeting, one of your colleague, let's call her Alice, privacy focused, raises
that one of our data warehouse table contains personal identifiable information (PII).
She checked with the security team and that violates the data processing agreement we have 
with them.

Pro-actively you volunteer to help solving the problem. Alice gives you a quick summary of the current 
infrastructure.


## The current infrastructure

A third-party system (TPCDS_SF10TCL) is doing a full data export to an object storage daily.
For simplicity, in this exercise the object storage is your local file system.
The export is in a [JSON Lines](https://jsonlines.org/) format and each line corresponds to a 
record in the source system.
That daily export is then processed and loaded to the data warehouse. This loading step keep the history 
of each record because our analysts need to be able to report on historical values.

Alice mentions that some other exports go through a transformation step to remove or transform some of 
these PII. Transformed exports are then loaded in the data warehouse.


## What to do?

Using your prefered language, process the files in the `data` directory to:
- Remove the `C_FIRST_NAME`, `C_LAST_NAME` properties of each JSON object.
- Extract the domain from `C_EMAIL_ADDRESS`, store it in `C_EMAIL_DOMAIN` and delete the original field.
- Write the resulting output to another file.

Once you are done with these transformations, explain how you would handle loading the results 
to an OLAP system, keeping each records historical values.


## Remarks

We expect to be able to easily run the transformation step locally.


## Sources

The sample dataset is a subset of the [TPC-DS benchmark](http://www.tpc.org/tpc_documents_current_versions/pdf/tpc-ds_v2.5.0.pdf)
available as sample data in [Snowflake](https://docs.snowflake.com/en/user-guide/sample-data-tpcds.html).
