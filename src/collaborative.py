import streamlit as st
import pandas as pd
from datetime import datetime
import json
import uuid
from ui import section_header

def show_collaboration():
    section_header("Collaborative Analytics", "Team collaboration, workspaces, and model management.")

    # Initialize session state for collaborative features
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "workspaces" not in st.session_state:
        st.session_state.workspaces = []
    if "model_versions" not in st.session_state:
        st.session_state.model_versions = []
    if "peer_reviews" not in st.session_state:
        st.session_state.peer_reviews = []

    # Create tabs for different collaborative features
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Team Notes", "🏢 Shared Workspaces", "📊 Model Version Control", "🔍 Peer Review"])

    with tab1:
        show_team_notes()

    with tab2:
        show_shared_workspaces()

    with tab3:
        show_model_version_control()

    with tab4:
        show_peer_review_system()

def show_team_notes():
    st.subheader("Team Notes & Insights")

    # Input form
    with st.form("note_form"):
        author = st.text_input("Your Name", "Anonymous")
        note_content = st.text_area("Add a Note / Insight")
        note_category = st.selectbox("Category", ["General", "Data Insights", "Model Performance", "Business Impact", "Technical Issues"])
        submitted = st.form_submit_button("Post Note")

        if submitted and note_content:
            new_note = {
                "id": str(uuid.uuid4()),
                "author": author,
                "content": note_content,
                "category": note_category,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "likes": 0
            }
            st.session_state.notes.append(new_note)
            st.success("Note added!")

    st.markdown("---")

    # Filter notes
    categories = ["All"] + list(set(note["category"] for note in st.session_state.notes))
    selected_category = st.selectbox("Filter by Category", categories, key="note_filter")

    # Display notes
    if not st.session_state.notes:
        st.info("No notes yet. Be the first to add one!")
    else:
        filtered_notes = [note for note in st.session_state.notes if selected_category == "All" or note["category"] == selected_category]

        for i, note in enumerate(reversed(filtered_notes)):
            with st.expander(f"{note['category']} | {note['timestamp']} | {note['author']}", expanded=False):
                st.write(note['content'])
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"👍 Like ({note['likes']})", key=f"like_{note['id']}"):
                        note['likes'] += 1
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{note['id']}"):
                        st.session_state.notes = [n for n in st.session_state.notes if n['id'] != note['id']]
                        st.rerun()

    # Export Notes
    if st.session_state.notes:
        notes_df = pd.DataFrame(st.session_state.notes)
        csv = notes_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Notes (CSV)", csv, "collaboration_notes.csv", "text/csv")

def show_shared_workspaces():
    st.subheader("Shared Workspaces")

    # Create new workspace
    with st.expander("Create New Workspace", expanded=False):
        with st.form("workspace_form"):
            ws_name = st.text_input("Workspace Name")
            ws_description = st.text_area("Description")
            ws_members = st.text_input("Team Members (comma-separated)", placeholder="user1@example.com, user2@example.com")
            ws_tags = st.text_input("Tags (comma-separated)", placeholder="machine-learning, customer-analytics")
            submitted = st.form_submit_button("Create Workspace")

            if submitted and ws_name:
                new_workspace = {
                    "id": str(uuid.uuid4()),
                    "name": ws_name,
                    "description": ws_description,
                    "members": [m.strip() for m in ws_members.split(",") if m.strip()],
                    "tags": [t.strip() for t in ws_tags.split(",") if t.strip()],
                    "created_by": "Current User",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "datasets": [],
                    "models": [],
                    "notebooks": []
                }
                st.session_state.workspaces.append(new_workspace)
                st.success(f"Workspace '{ws_name}' created!")

    st.markdown("---")

    # Display workspaces
    if not st.session_state.workspaces:
        st.info("No workspaces created yet. Create your first workspace above!")
    else:
        for workspace in st.session_state.workspaces:
            with st.expander(f"🏢 {workspace['name']} - {len(workspace['members'])} members", expanded=False):
                st.write(f"**Description:** {workspace['description']}")
                st.write(f"**Created by:** {workspace['created_by']} on {workspace['created_at']}")
                st.write(f"**Members:** {', '.join(workspace['members'])}")
                if workspace['tags']:
                    st.write(f"**Tags:** {', '.join(workspace['tags'])}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Datasets", len(workspace['datasets']))
                with col2:
                    st.metric("Models", len(workspace['models']))
                with col3:
                    st.metric("Notebooks", len(workspace['notebooks']))

def show_model_version_control():
    st.subheader("Model Version Control")

    # Register new model version
    with st.expander("Register New Model Version", expanded=False):
        with st.form("model_version_form"):
            model_name = st.text_input("Model Name")
            version = st.text_input("Version (e.g., v1.0.0)")
            algorithm = st.selectbox("Algorithm", ["Random Forest", "XGBoost", "LightGBM", "Neural Network", "Linear Regression", "SVM", "Other"])
            accuracy = st.number_input("Accuracy Score", 0.0, 1.0, 0.85)
            description = st.text_area("Description / Changes")
            submitted = st.form_submit_button("Register Version")

            if submitted and model_name and version:
                new_version = {
                    "id": str(uuid.uuid4()),
                    "model_name": model_name,
                    "version": version,
                    "algorithm": algorithm,
                    "accuracy": accuracy,
                    "description": description,
                    "created_by": "Current User",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Active"
                }
                st.session_state.model_versions.append(new_version)
                st.success(f"Model version {version} registered!")

    st.markdown("---")

    # Display model versions
    if not st.session_state.model_versions:
        st.info("No model versions registered yet.")
    else:
        # Group by model name
        model_groups = {}
        for version in st.session_state.model_versions:
            model_name = version['model_name']
            if model_name not in model_groups:
                model_groups[model_name] = []
            model_groups[model_name].append(version)

        for model_name, versions in model_groups.items():
            with st.expander(f"🤖 {model_name} - {len(versions)} versions", expanded=False):
                versions_df = pd.DataFrame(versions)
                st.dataframe(versions_df[['version', 'algorithm', 'accuracy', 'created_at', 'status']], use_container_width=True)

                # Show latest version details
                latest = max(versions, key=lambda x: x['created_at'])
                st.markdown("**Latest Version Details:**")
                st.write(f"Version: {latest['version']}")
                st.write(f"Algorithm: {latest['algorithm']}")
                st.write(f"Accuracy: {latest['accuracy']:.3f}")
                st.write(f"Description: {latest['description']}")

def show_peer_review_system():
    st.subheader("Peer Review System")

    # Submit for review
    with st.expander("Submit Model for Review", expanded=False):
        with st.form("review_form"):
            review_title = st.text_input("Review Title")
            model_name = st.text_input("Model Name")
            reviewer_email = st.text_input("Reviewer Email")
            review_description = st.text_area("Description of what needs review")
            submitted = st.form_submit_button("Submit for Review")

            if submitted and review_title and reviewer_email:
                new_review = {
                    "id": str(uuid.uuid4()),
                    "title": review_title,
                    "model_name": model_name,
                    "reviewer_email": reviewer_email,
                    "description": review_description,
                    "submitted_by": "Current User",
                    "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Pending",
                    "feedback": ""
                }
                st.session_state.peer_reviews.append(new_review)
                st.success("Model submitted for review!")

    st.markdown("---")

    # Display reviews
    if not st.session_state.peer_reviews:
        st.info("No reviews submitted yet.")
    else:
        for review in st.session_state.peer_reviews:
            status_color = {"Pending": "orange", "In Review": "blue", "Approved": "green", "Rejected": "red"}.get(review['status'], "grey")

            with st.expander(f"🔍 {review['title']} - Status: {review['status']}", expanded=False):
                st.write(f"**Model:** {review['model_name']}")
                st.write(f"**Reviewer:** {review['reviewer_email']}")
                st.write(f"**Submitted by:** {review['submitted_by']} on {review['submitted_at']}")
                st.write(f"**Description:** {review['description']}")

                if review['status'] == "Pending":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Start Review", key=f"start_{review['id']}"):
                            review['status'] = "In Review"
                            st.rerun()
                    with col2:
                        if st.button("Cancel", key=f"cancel_{review['id']}"):
                            st.session_state.peer_reviews = [r for r in st.session_state.peer_reviews if r['id'] != review['id']]
                            st.rerun()

                elif review['status'] == "In Review":
                    feedback = st.text_area("Review Feedback", value=review.get('feedback', ''), key=f"feedback_{review['id']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Approve", key=f"approve_{review['id']}"):
                            review['status'] = "Approved"
                            review['feedback'] = feedback
                            st.success("Model approved!")
                            st.rerun()
                    with col2:
                        if st.button("Reject", key=f"reject_{review['id']}"):
                            review['status'] = "Rejected"
                            review['feedback'] = feedback
                            st.error("Model rejected!")
                            st.rerun()
                    with col3:
                        if st.button("Save Feedback", key=f"save_{review['id']}"):
                            review['feedback'] = feedback
                            st.success("Feedback saved!")

                if review.get('feedback'):
                    st.markdown("**Review Feedback:**")
                    st.info(review['feedback'])
