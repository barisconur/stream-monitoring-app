import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";

import App from "./App";
import Statistics from "./components/Statistics"
import ChunksTable from "./components/ChunksTable"

export default function Routing() {
  return (
    <Router>
        <Switch>
          <Route exact path="/">
            <App />
          </Route>
          <Route path="/statistics">
            <Statistics/>
          </Route>

          <Route path="/:id/chunks" component={ChunksTable}/>

        </Switch>
    </Router>
  );
}