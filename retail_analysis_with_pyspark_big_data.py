from pyspark.sql import SparkSession
import numpy as np
import pandas as pd
import json
import pyspark.sql.functions as F
import pyspark.sql
from pyspark.sql.functions import col, skewness, kurtosis
from pyspark.context import SparkContext
from pyspark.sql.functions import *
from pyspark.sql.functions import isnan, when, count, col
from pyspark.sql.functions import when
from pyspark.sql.functions import UserDefinedFunction
from pyspark.sql.functions import from_unixtime, unix_timestamp
from pyspark.sql.types import StringType
from datetime import date, timedelta, datetime
import time

spark = SparkSession.builder.getOrCreate()

"""Note that the Spark version used for here is 2.4.5, which can be found by the command `spark.version`."""

def load_data(data):
    """data="online1.csv" or "online2.csv" """
    t1=time.time()
    dat = spark.read.options(header=True, inferSchema=True).csv(data)
    t2=time.time()
    print("Duration:", np.round((t2-t1), 2), "seconds")
    return(dat)

df1 = load_data('order.txt.csv')

df2 = load_data('order.txt.csv')

df = df1.unionByName(df2)

datashape(df)

df.limit(5).show()

"""This is the traditional Spark DataFrame output.
By using the following setting we will get from now on a Pandas-like output.
"""

spark.conf.set("spark.sql.repl.eagerEval.enabled", True)

"""![image.png](data:image/png;base64,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)

A number of descriptive statistics can be obtained, like count, standard deviation, mean, minimum and maximum.
"""

summary = df.describe().toPandas()
summary = summary.T
summary.columns = summary.iloc[0]
summary = summary.drop(summary.index[0])
summary

"""The table column *count* suggests that there are missing values in *Description* and *Customer ID*. The number of NaN is displayed by the following code:"""

df.select([count(when(isnan(c) | col(c).isNull(), c)).alias(c) for c in df.columns])

"""Cancelled transactions start with a capital C in the column Invoice. These will be removed by the following."""

df = df[~df['Invoice'].startswith("C")]

"""The datashape function confirms that cancelled transactions have been removed."""

datashape(df)

"""**CHANGING NAME AND DATA TYPE**

The columnname *Customer ID* contains an annoying white space that under certain circumstances can cause problems. So we should better rename that.
"""

df = df.withColumnRenamed('Customer ID', 'CustomerID')

"""Further, the *Country* EIRE can be replaced by Ireland. The result can be verified by `df.filter(df.Country == "Ireland").limit(5)`"""

df = df.replace(['EIRE'],['Ireland'])

"""Information about the column type can be obtained. If you want some supplementary information, an alternative command is `df.explain(df)` ."""

df.schema

"""Knowing the column types, we could now cast the column Quantity from integer to float."""

df = df.withColumn("Quantity", col("Quantity").cast("Float"))

"""The *InvoiceDate* shows up as a string. In order to exploit the time-related information, it would be best to convert it to date type. We will do this by creating a new column *n_InvoiceDate*."""

df = df.withColumn("n_InvoiceDate", from_unixtime(unix_timestamp('InvoiceDate', 'MM/dd/yyyy HH:mm')).alias('n_InvoiceDate'))

"""Sorting the new dates, we can now display the number of records (rows) as a function of date and time.

It is also possible to display a range of dates. The following spots all sales at 15 Jan 2010 from 8 till 10 o'clock.
"""

df[(df["n_InvoiceDate"]> '2010-01-15 08:00:00') & (df["n_InvoiceDate"]< '2010-01-15 10:00:00') ]

"""**CONVERTING DATA**

Time-serie analyses often require different time units, like seconds, minutes, hours, days, weeks, months, years. For example, if we want to display the sales per week, we could use the function `weekofyear` that translates the date to week.
"""

df = df.withColumn("weekofyear", weekofyear("n_InvoiceDate"))

"""Multiple columns can be used in a computation. The total *Amount* a customer spent can be computed by multiplication of the *Price* of a single product with its *Quantity*."""

df = df.withColumn("Amount", col("Quantity") * col("Price"))
df.limit(5)

"""**FILTERING DATA**

How to select rows that contain specific products? We can use the command `isin`, which is very similar to the Pandas isin function:
"""

df[df.Description.isin('WHITE HANGING HEART T-LIGHT HOLDER')].limit(5)

"""If we want to search our data by key word, we would use the command `like`."""

df[df.Description.like('%WHITE%')].limit(5)

"""To find big buyers, probably organizational customers, select rows where *Quantity* is larger than 50000. Note that `df.where(df.Quantity > 50000)` would give a similar result."""

df.filter(df.Quantity > 50000)

"""Let us count the number of data records per country and sort the output, which shows that UK is clearly leading the list.

Sort can be used for *InvoiceDate* as well. This can show which hours customers purchase preferentially.
"""

df.groupby("n_InvoiceDate").count().sort("n_InvoiceDate", ascending=True).limit(10)

"""**USING SQL IN PYSPARK**"""

df.registerTempTable("df")

spark.sql("select Description, Quantity from df").limit(5)

"""Select the columns *Description* and *Quantity* and only those rows where *Quantity* has value = 6"""

spark.sql("select Description, Quantity from df where Quantity = 6").limit(5)

"""Select the columns *Description*, *Quantity*, and *Country* where *Quantity* has value = 6 and *country* is United Kingdom."""

spark.sql("select Description, Quantity, Country from df where Quantity=6 AND Country = 'United Kingdom'").limit(5)

"""SQL can also be used to show distinct (unique) values in a column. To limit space, only five are displayed here.

And we can count the number of distinct values, that is how many countries are in total in the data.
"""

spark.sql("SELECT COUNT(DISTINCT Country) from df")

"""Using SQL we can also exclude certain values. For example, exclude all records with United Kingdom."""

spark.sql("select Description, Quantity, Country from df where Quantity=6 AND NOT Country = 'United Kingdom'").limit(5)

"""It would be possible to add a new column that categorizes UK (1) or not-UK (0). You could then use `df.filter(df.Country == "United Kingdom").limit(5)` and `filter(df.Country == "France").limit(5)` to check if the column is correctly coding UK versus not-UK."""

df = df.withColumn('Country_UK', F.lit(0))
df = df.withColumn("Country_UK", when(df["Country"] == 'United Kingdom', 1).otherwise(df["Country_UK"]))

"""Next, we could count UK versus not-UK using the new column Country_UK."""

df.groupBy("Country_UK").count()

"""And compute mean *Amount* and summed *Quantity*."""

df.groupBy("Country_UK").agg({"Amount": "mean", "Quantity": "sum"})
