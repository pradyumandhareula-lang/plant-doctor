with tab2:
    st.header("📋 Past Diagnostic Records")
    st.write("Review past historical plant logs compiled inside the system.")
    
    try:
        # Fetch data from backend database endpoint
        history_url = "http://127.0.0.1.8001"
        response = requests.get(history_url)
        
        if response.status_code == 200:
            records = response.json().get("history", [])
            
            if not records:
                st.info("No scan history found yet. Run your first scan in the 'New Scan' tab!")
            else:
                for record in records:
                    # Create an expandable box layout for each past record card
                    with st.expander(f"🌱 {record['species']} — {record['timestamp']}"):
                        st.subheader(f"Health Status: {record['issue']}")
                        st.markdown(f"**Treatment Plan:**\n{record['plan']}")
        else:
            st.error("Could not load history metrics from backend pipeline.")
            
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
