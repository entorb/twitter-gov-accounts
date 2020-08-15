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
                title: "Bundesland<br/>&nbsp;<br/>&nbsp;", field: "BL_Name", sorterParams: {
                    alignEmptyValues: "bottom"
                }, width: 150, headerFilter: true
            },
            { title: "Landkreis<br/>&nbsp;<br/>&nbsp;", field: "LK_Name", sorter: "string", headerFilter: true },
            { title: "Landkreis<br/>&nbsp;<br/>&nbsp;", field: "LK_Type", sorter: "string", headerFilter: true },

        ],
        // rowClick: function (e, row) {
        //     var rowData = row.getData();
        //     // console.log(row._row);
        //     // console.log(rowData);

        //     var clickedCode = rowData["LK_ID"];
        //     var clickedDistrict = rowData["Landkreis"];
        //     if (row._row.modules.select.selected == true) {
        //         addRegion(clickedCode);
        //         alert(clickedDistrict + " zur Auswahl hinzugefügt")
        //     } else {
        //         removeRegion(clickedCode);
        //         alert(clickedDistrict + " von Auswahl entfernt")
        //     }

        //     // var selectedRows = table.getSelectedRows();
        //     // console.log(selectedRows);
        // },
    });

    table.setSort([
        { column: "Landkreis", dir: "asc" },
        { column: "Bundesland", dir: "asc" },
        { column: "Cases_Last_Week_Per_100000", dir: "desc" }, //sort by this first
    ]);

    return table;
}