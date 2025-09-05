#!/usr/bin/env python3
"""
Blog Analyzer Script
Analyzes the current blogs and counts how many are empty.
"""

import json
import os

def analyze_blogs():
    """Analyze blogs from blogBase.json and provide statistics."""
    
    # Read the blogBase.json file
    blog_base_path = 'blogBase.json'
    if not os.path.exists(blog_base_path):
        print("Error: blogBase.json file not found!")
        return
    
    with open(blog_base_path, 'r', encoding='utf-8') as f:
        blog_data = json.load(f)
    
    # Extract post list from the data
    post_list = blog_data.get('postListJson', {})
    
    if not post_list:
        print("No posts found in blogBase.json")
        return
    
    print("=== BLOG ANALYSIS REPORT ===\n")
    
    # Count total blogs
    total_blogs = len(post_list)
    print(f"Total number of blogs: {total_blogs}")
    
    # Analyze each blog
    empty_blogs = []
    non_empty_blogs = []
    
    print("\n=== ALL CURRENT BLOGS ===")
    for post_id, post_data in post_list.items():
        title = post_data.get('postTitle', 'No Title')
        word_count = post_data.get('wordCount', 0)
        description = post_data.get('description', '').strip()
        created_date = post_data.get('createdDate', 'Unknown Date')
        labels = post_data.get('labels', [])
        
        # Determine if blog is empty
        is_empty = word_count == 0 or not description
        
        print(f"\n{post_id}: {title}")
        print(f"  Created: {created_date}")
        print(f"  Word Count: {word_count}")
        print(f"  Labels: {', '.join(labels) if labels else 'None'}")
        print(f"  Description: {description[:100] + '...' if len(description) > 100 else description or '(Empty)'}")
        print(f"  Status: {'EMPTY' if is_empty else 'HAS CONTENT'}")
        
        if is_empty:
            empty_blogs.append({
                'id': post_id,
                'title': title,
                'date': created_date,
                'word_count': word_count
            })
        else:
            non_empty_blogs.append({
                'id': post_id,
                'title': title,
                'date': created_date,
                'word_count': word_count
            })
    
    # Summary statistics
    empty_count = len(empty_blogs)
    non_empty_count = len(non_empty_blogs)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total blogs: {total_blogs}")
    print(f"Empty blogs: {empty_count}")
    print(f"Blogs with content: {non_empty_count}")
    print(f"Empty blog percentage: {(empty_count/total_blogs)*100:.1f}%")
    
    # List empty blogs
    if empty_blogs:
        print(f"\n=== EMPTY BLOGS ({empty_count}) ===")
        for blog in empty_blogs:
            print(f"- {blog['id']}: {blog['title']} (Created: {blog['date']})")
    
    # List blogs with content
    if non_empty_blogs:
        print(f"\n=== BLOGS WITH CONTENT ({non_empty_count}) ===")
        for blog in non_empty_blogs:
            print(f"- {blog['id']}: {blog['title']} (Words: {blog['word_count']}, Created: {blog['date']})")

if __name__ == "__main__":
    analyze_blogs()