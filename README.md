# Assignment - Zivver

## The story

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
