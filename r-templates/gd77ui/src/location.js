import React, { Component } from 'react';
import range from './utils.js';
import gd77store from './store.js';

let data = [
    {
        country: 'Polska',
        short: 'PL',
        amin: 1,
        amax: 9,
        prefixes: ['A', 'B', 'C']
    },
    {
        country: 'Niemcy',
        short: 'DE',
        amin: 0,
        amax: 9,
        prefixes: ['A', 'B', 'C']
    }
]

class Figure extends Component {
    constructor(props) {
        super(props);
        this.size = this.props.big === "1" ? '64x64' : '48x48';
        this.mag = this.props.big === "1" ? '3x' : '2x';
    }

    render() {
      return (
        <figure className="media-left">
          <p className={`image is-${this.size}`}>
            <i className={`${this.props.fas} fa-${this.props.icon} fa-${this.mag}`}></i>
          </p>
        </figure>
      );
    }
}

class Header extends Component {
    render() {
      return (
        <div className="content">
            <p>
            <strong>{this.props.title}</strong>
            <br/>
            {this.props.subtitle}
            <br/>
            </p>
        </div>
      );
    }
}


class Button extends Component {
    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.name = props.name;
        this.type = props.type;
        this.state = {
            country: props.country,
            selected: false
        }
    }

    handleClick() {
        this.setState({selected: !this.state.selected});
        let action = (!this.state.selected ? 'SELECT_' : 'UNSELECT_') + this.type;
        gd77store.dispatch({
            country: this.state.country,
            type: action,
            prefix: this.name,
            area: this.name
        });
    }

    render () {
        let classes = 'button is-normal is-rounded is-dark spread ' + (this.state.selected ? '' : 'is-outlined');
        return (
          <a className={`${classes}`} onClick={this.handleClick}>{this.props.name}</a>
        );
    }
}


class ButtonPanel extends Component {
    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.content = props.buttons || (<i>(brak danych)</i>);
        this.country = props.country;
    }

    handleClick() {
        console.log(this.props.children);
        if (!Array.isArray(this.content)) {
            return;
        }

    }

    render() {
        return (
            <tr>
                <td><a onClick={this.handleClick}>{this.props.title}</a></td>
                <td className="monosp">
                    {this.content}
                </td>
            </tr>   
        );
    }
}

function make_buttons(data, country) {
    const prfx = data.prefixes.map((button_name, i) =>
        <Button name={button_name} key={i} country={country} type='PREFIX'/>
    );
    if (!data.amin || !data.amax) {
        return [ prfx, null];
    }
    
    let r = range(data.amin, data.amax);
    const areas = r.map((button_name, i) =>
        <Button name={button_name} key={i} country={country} type='AREA'/>
    );

    return [prfx, areas];
}


class CountrySection extends Component {
    constructor(props) {
      super(props);
      this.name = props.data.country;
      this.country = props.data.short;
      this.buttons = make_buttons(props.data, this.country);
      this.prefix_buttons = this.buttons[0];
      this.area_buttons = this.buttons[1];
    }

    render () {
        return (
          <article className="media">
            <Figure fas="fas" icon="map-marker-alt" big="0" />
            <div className="media-content">
              <div className="content"><p><strong>{this.name}</strong></p></div>
              <article className="media">
                <table className="table">
                <tbody>
                  <ButtonPanel title="Prefixy" buttons={this.prefix_buttons} country={this.name} />
                  <ButtonPanel title="Okręgi wywoławcze" buttons={this.area_buttons} country={this.name} />
                </tbody>
                </table>
              </article>
            </div>
          </article>
        );
    }
}

class LocationPage extends Component {
    render () {
      let countries = data.map((country, i) => <CountrySection data={country} key={i} />);
      return (
        <article className="media">
            <Figure fas="fas" icon="map-signs" big="1" />
            <div className="media-content">
                <Header title="Lokalizacja" subtitle="lorem ipsum" />
                {countries}
            </div>
        </article>
      );
    }
}

export default LocationPage;