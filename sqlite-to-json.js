var args = process.argv.slice(2);
if (args.length == 0) {
  console.log("Needs argument.");
  process.exit(1);
}

sqliteFile = args[0]

const SqliteToJson = require('sqlite-to-json');
const sqlite3 = require('sqlite3');
const exporter = new SqliteToJson({
  client: new sqlite3.Database(sqliteFile)
});

exporter.tables(function (err, tables) {
  tables.forEach(function(table) {
    exporter.save(table, './export/' + table + '.json', function (err) {
      if (err) {
        console.log(err);
      }
    });
  });
});
