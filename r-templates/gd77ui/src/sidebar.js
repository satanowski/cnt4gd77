import React, { Component } from 'react';
import { Route, Link } from "react-router-dom";
// import gd77store from './store.js';

const menu_map = [
    {
        name: 'Ogólne',
        fa: 'far',
        icon: 'window-maximize',
        items: [
            {fa: 'fas', icon: 'info', name: 'Info', id: 'INFO'},
            {fa: 'far', icon: 'comment', name: 'Komentarze', id: 'COMMENTS'}
        ]
    },
    {
        name: 'Kontakty',
        icon: 'users',
        items: [
            {fa: 'fas', icon: 'map-signs', name: 'Lokalizacja', id: 'LOCATION'},
            {fa: 'fas', icon: 'phone', name: 'Grupy rozm.', id: 'TALKGROUPS'},
            {fa: 'fas', icon: 'user-secret', name: 'Specjalne', id: 'SPEC_CONTACT'},
            {fa: 'far', icon: 'address-book', name: 'Priorytetowe', id: 'PRIO_CONTACTS'},
            {fa: 'fas', icon: 'address-book', name: 'Ignorowane', id: 'IGNOR_CONTACTS'},
            {fa: 'fas', icon: 'database', name: 'Słownik', id: 'DICTIONARY'}
        ]
    },
    {
        name: 'Kanały',
        icon: 'server',
        items: [
            {fa: 'fas', icon: 'industry', name: 'Przemienniki', id: 'REPEATERS'},
            {fa: 'fas', icon: 'train', name: 'PKP', id: 'PKP'},
            {fa: 'fas', icon: 'subway', name: 'Metro', id: 'METRO'},
            {fa: 'fas', icon: 'phone-volume', name: 'PMR', id: 'PMR_ANA'},
            {fa: 'fas', icon: 'tty', name: 'PMR Digi', id: 'PMR_DIG'},
        ]
    },
    {
        name: 'CSV',
        icon: 'table',
        items: [
            {fa: 'fas', icon: 'magic', name: 'Generuj!', id: 'GENERATE'}
        ]
    }
];

class MenuLabel extends Component {
    constructor(props) {
        super(props);
        this.fa = props.fa || "fa";
    }

    render () {
        return (
            <p className="menu-label">
              <i className={`${this.fa} fa-${this.props.icon}`}></i>
              &nbsp;{this.props.name}
            </p>
        );
    }
}


const MenuLink = ({ label, to, activeOnlyWhenExact, fa, icon }) => (
    <Route
      path={to}
      exact={activeOnlyWhenExact}
      children={({ match }) => (
        <li>
          <Link to={to}>
              <span className="icon">
                <i className={`${fa} fa-${icon}`}></i>
              </span>
              &nbsp;{label}
          </Link>
        </li>
      )}
    />
  );
  

class MenuSection extends Component {
    render () {
        const ml = <MenuLabel fas={this.props.fa} icon={this.props.icon} name={this.props.name} />
        const items = this.props.items.map((item, i) =>
            <MenuLink
                to={`/${item.id.toLowerCase()}`}
                label={item.name}
                fa={item.fa}
                icon={item.icon}
                key={i}
            />
        );
        
        return (
            <div>{ml}<ul className="menu-list">{items}</ul></div>
        );

    }
}


const menu = menu_map.map( (section, i) =>
    <MenuSection fa={section.fa} icon={section.icon} name={section.name} items={section.items} key={i} />
);


class Sidebar extends Component {
  render() {
    return (
      <aside className="menu" style={{position:'sticky', top:'10px'}}>
        {menu}
      </aside>
    );
  }
}

export default Sidebar;