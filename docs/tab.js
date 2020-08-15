// ASync JQuery fetching
function fetch_table_data() {
    table.setData("https://entorb.net/COVID-19-coronavirus/data/de-districts/de-districts-results-V2.json", {}, "get")
}

function defineTable() {
    var table = new Tabulator("#table-de-districts", {
        height: 600, // set height of table to enable virtual DOM
        layout: "fitColumns", //fit columns to width of table (optional)
        // autoColumns: true, // very nice!!!
        tooltipsHeader: true,
        selectable: true,
        columns: [ //Define Table Columns
            // not using the checkbox column, as clicking the checkbox is not the same as clicking the row
            // { formatter: "rowSelection", titleFormatter: "rowSelection", align: "center", headerSort: true },
            {
                title: "Land", field: "BL_Code", sorterParams: {
                    alignEmptyValues: "bottom"
                }, width: 50, headerFilter: true
            },
            { title: "Landkreis", field: "LK_Name", sorter: "string", headerFilter: true },
            { title: "Art", field: "LK_Type", sorter: "string", headerFilter: true },
            {
                title: "Einwohner", field: "Population", sorter: "number", width: 130, hozAlign: "right", sorterParams: {
                    alignEmptyValues: "bottom"
                }, headerFilter: true, headerFilterPlaceholder: "filter >=", headerFilterFunc: ">=",
            },
            {
                title: "Tweets", field: "Twitter Tweets", sorter: "number", width: 130, hozAlign: "right", sorterParams: {
                    alignEmptyValues: "bottom"
                }, headerFilter: true, headerFilterPlaceholder: "filter >=", headerFilterFunc: ">=",
            },
            {
                title: "Follower", field: "Twitter Follower", sorter: "number", width: 130, hozAlign: "right", sorterParams: {
                    alignEmptyValues: "bottom"
                }, headerFilter: true, headerFilterPlaceholder: "filter >=", headerFilterFunc: ">=",
            },

        ],
        rowClick: function (e, row) {
            var rowData = row.getData();
            if ('Twitter URL' in rowData === true) {
                var activityUrl = rowData["Twitter URL"];
                window.open(activityUrl);
            }
        },
    });

    table.setSort([
        { column: "Twitter Tweets", dir: "desc" },
    ]);

    return table;
}