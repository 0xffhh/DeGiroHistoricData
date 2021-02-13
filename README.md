# De Giro Historic Data
Some python code to function as Azure function, which fetches and stores your portfolio data for generating reports based on daily data. 

This is not a point-and-click install. Requires some manual work to get deploy it as an Azure function. You can also opt to run it as a cron-job on some kind of server. The only requirement is an internet connection and a SQL Server (Express) database. 

This data allows you to track your portfolio details over time, a feature which De Giro doesn't offer. Im using it for generating PowerBI reports. This is how it looks like, approximately. 
