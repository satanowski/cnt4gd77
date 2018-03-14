import React, { Component } from 'react';
import { BrowserRouter as Router, Route} from "react-router-dom";
import './App.css';
import TopPanel from './top_panel.js';
import Sidebar from './sidebar.js';
import LocationPage from './location.js';
import InfoPage from './info.js';
import Comments from './comments.js';


class App extends Component {

  constructor(props) {
    super(props);
    this.state = { }
  }

  render() {
    return (
      <section className="section">
        <div className="container">
          <TopPanel title="GD-77" subtitle="Generator kontaktów i kanałów"/>
          <section className="section" style={{border:'1px solid #ccc', borderTop:'none'}}>
            <div className="container" style={{width: 'auto'}}>
              <Router>
              <div className="columns">
                <div className="column is-one-fifth">
                  <Sidebar />
                </div>
                <div className="column">
                  <Route path="/info" component={InfoPage} />
                  <Route path="/location" component={LocationPage} />
                  <Route path="/comments" component={Comments} />
                </div>
              </div>
              </Router>
            </div>
          </section>
        </div>
      </section>
    );
  }
}


export default App;
