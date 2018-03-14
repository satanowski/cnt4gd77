import React, { Component } from 'react';

const version = '0.9.7';
const last_data = '2018.01.23';
const last_update = '2018.01.24';

class Card extends Component {
    render() {
        return (
          <div className="card">
            <div className="card-content">
              <div className="media">
                <div className="media-left">
                  <figure className="image is-48x48">
                    <i className={`fa fa-${this.props.icon} fa-2x`} aria-hidden="true"></i>
                  </figure>
                </div>
                <div className="content">
                  <p className="title is-4">{this.props.title}</p>
                  <p className="subtitle is-6 tall">{this.props.content}</p>
                </div>
              </div>
            </div>
          </div>
        );
    }
}

class InfoPage extends Component {
    render () {
      return (
        <div>
          <Card icon="code-branch" title="Wersja" content={version} />
          <Card icon="pencil-alt" title="Ostatnia aktualizacja kodu" content={last_update} />
          <Card icon="database" title="Ostatnia aktualizacja danych" content={last_data} />
          <Card icon="bug" title="Gdzie zgłaszać błędy i pomysły"
            content="https://github.com/satanowski/cnt4gd77/issues"
          />
          <Card icon="users" title="Tworzyli i pomagali"
            content="SP5DRS, SP5TA, SQ5AZQ"
          />
        </div>
      );
    }
}

export default InfoPage;