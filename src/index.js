import React, { useState } from "react"
import ReactDOM from "react-dom"
import ReactDataGrid from "react-data-grid"
import data from "./vote_data.json"
import "./index.css"

const defaultColumnProperties = {
  sortable: false,
  width: 140,
}

const columnMap = {
  index: {
    name: "Index",
    width: 80,
    sortDescendingFirst: true,
  },
  preferred_name: {
    name: "Name",
    sortable: true,
    width: 230,
  },
  state: {
    name: "State",
    sortable: true,
    filterable: true,
    width: 80,
  },
  electorate: {
    name: "Electorate",
  },
  votes: {
    name: "Climate Votes",
    sortable: true,
  },
  // twitter: {
  //   name: "Twitter",
  //   // sortable: true,
  // },
  // fbook: {
  //   name: "Facebook",
  //   sortable: true,
  // },
  Party: {
    name: "Party",
    sortable: true,
    filterable: true,
  },
  Swing: {
    name: "2019 Swing (%)",
    sortable: true,
  },
  Margin: {
    name: "2019 Margin (%)",
    sortable: true,
  },
  Vote_diff: {
    name: "2019 Margin",
    sortable: true,
  },
  Participation: {
    name: "Climate Participation (%)",
    sortable: true,
  },
}

const getColumns = d =>
  d.schema.fields.map(i => ({
    key: i["name"],
    ...defaultColumnProperties,
    ...columnMap[i["name"]],
  }))

const sortRows = (initialRows, sortColumn, sortDirection) => rows => {
  const comparer = (a, b) => {
    console.log(sortDirection, sortColumn, a[sortColumn], b[sortColumn])
    if (sortDirection === "ASC") {
      return a[sortColumn] > b[sortColumn] ? 1 : -1
    } else if (sortDirection === "DESC") {
      return a[sortColumn] < b[sortColumn] ? 1 : -1
    }
  }

  return sortDirection === "NONE" ? initialRows : [...rows].sort(comparer)
}

const Grid = () => {
  const [rows, setRows] = useState(data.data)
  const columns = getColumns(data)

  return (
    <ReactDataGrid
      columns={columns}
      rowGetter={i => rows[i]}
      rowsCount={rows.length}
      enableCellSelect={true}
      minHeight={600}
      onGridSort={(sortColumn, sortDirection) =>
        setRows(sortRows(data.data, sortColumn, sortDirection))
      }
    />
  )
}

const App = () => (
  <div className="App">
    <h2>Climate Action Australia Vote Data</h2>
    <h3>
      Vote at{" "}
      <a href="https://www.climateactnow.com.au/">climateactnow.com.au</a>
    </h3>
    <p>
      Click column headings to sort. Double click to filter. [
      <a href="https://github.com/4dwins/climatevotedata">code</a>] [
      <a href="https://twitter.com/4dwins">@4dwins</a>]
    </p>
    <Grid />
  </div>
)

const rootElement = document.getElementById("root")
ReactDOM.render(<App />, rootElement)
