document.getElementById("export-btn").addEventListener("click", function() {
    // Créer une instance de tableau Excel
    let table = document.getElementById("tableGrid3");
    // Créer une nouvelle instance de workbook Excel
    let workbook = XLSX.utils.table_to_book(table);
    // Convertir le workbook en binaire Excel
    let excelData = XLSX.write(workbook, {
    bookType: "xlsx",
    type: "array"
    });
    // Créer un objet blob avec les données Excel
    let blob = new Blob([excelData], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    });
    // Créer un objet URL pour le blob
    let url = URL.createObjectURL(blob);
    // Créer un lien et déclencher le téléchargement
    let a = document.createElement("a");
    a.href = url;
    a.download = "analyses.xlsx";
    a.click();
    // Libérer l'URL de l'objet blob
    URL.revokeObjectURL(url);
});