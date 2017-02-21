#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
from string import letters
import cgi
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    

    def render(self):

        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class ContentPage(BaseHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * from Post ORDER by created desc LIMIT 5")
        self.render('front.html', posts = posts)
class ViewPostHandler(BaseHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if not post:
            self.render('404.html', past = post_id)
            return

        self.render("permalink.html", post = post)

class CreatePost(BaseHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
        	
            post = Post(subject = subject, content = content)
            post.put()
            k=str(post.key().id())
            j= '/blog/' + k 

            self.redirect(j)
        else:
            error = "subject and content, required!"
            self.render("newpost.html", subject=subject, content=content, error=error)


app = webapp2.WSGIApplication([
    ('/blog', ContentPage),
    ('/blog/newpost', CreatePost),
    ('/blog/([0-9]+)', ViewPostHandler ),
    
], debug=True)
