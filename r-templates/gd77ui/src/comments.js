import React from 'react';
import ReactDisqusComments from 'react-disqus-comments';
 
class Comments extends React.Component {
  handleNewComment(comment) {
    console.log(comment.text);
  }
 
  render() {
    return (
      <ReactDisqusComments
        shortname="gd77"
        identifier="gd77"
        title="GD77 Thread"
        url="http://gd77.sp5drs.xyz"
        onNewComment={this.handleNewComment}/>
    );
  }
}


export default Comments;