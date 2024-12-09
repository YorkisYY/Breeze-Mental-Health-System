def update_mhwp_schedules(schedule_file=SCHEDULE_DATA_PATH, template_file=MHWP_SCHEDULE_TEMPLATE_PATH):
    today = datetime.now()
    week_starts = [
        today,  # Current week
        today + timedelta(weeks=1),  # Next week 
        today + timedelta(weeks=2),  # Week 3
        today + timedelta(weeks=3)   # Week 4
    ]
    
    # Read templates first
    templates_df = pd.read_csv(template_file)
    mhwp_users = templates_df['mhwp_username'].unique()
    
    # Read existing schedules if any
    existing_schedules = pd.read_csv(schedule_file) if os.path.exists(schedule_file) else pd.DataFrame()
    new_schedules = []
    
    for mhwp in mhwp_users:
        # Check if MHWP has existing schedule
        mhwp_schedule = existing_schedules[existing_schedules['mhwp_username'] == mhwp] if not existing_schedules.empty else pd.DataFrame()
        
        if mhwp_schedule.empty:
            # Generate full 4 weeks
            start_date = today
            end_date = week_starts[3] + timedelta(days=7)
        else:
            # Convert dates for comparison
            mhwp_schedule['Date'] = pd.to_datetime(mhwp_schedule['Date'], format='%Y/%m/%d')
            
            # Keep first 2 weeks only
            keep_schedules = mhwp_schedule[mhwp_schedule['Date'] < week_starts[2]]
            if not keep_schedules.empty:
                new_schedules.extend(keep_schedules.to_dict('records'))
            
            # Check weeks 3-4 for appointments
            for week_num in [2, 3]:
                week_schedule = mhwp_schedule[
                    (mhwp_schedule['Date'] >= week_starts[week_num]) & 
                    (mhwp_schedule['Date'] < (week_starts[week_num] + timedelta(days=7)))
                ]
                
                if not week_schedule.empty:
                    has_appointments = week_schedule.iloc[:, 3:].isin(["●"]).any().any()
                    if has_appointments:
                        print(f"\nWarning: Detected confirmed appointments for {mhwp} in Week {week_num + 1}")
                        print(f"Please cancel appointments for {week_starts[week_num].strftime('%Y/%m/%d')} - {(week_starts[week_num] + timedelta(days=6)).strftime('%Y/%m/%d')}")
                        return False
            
            # Update weeks 3-4
            start_date = week_starts[2] + timedelta(days=1)
            end_date = week_starts[3] + timedelta(days=7)
        
        # Generate new schedules for this MHWP
        mhwp_templates = templates_df[templates_df['mhwp_username'] == mhwp].to_dict('records')
        current_date = start_date
        while current_date < end_date:
            # Find matching template for current weekday
            day_template = next((t for t in mhwp_templates if int(t['weekday']) == current_date.weekday()), None)
            if day_template:
                schedule_entry = {
                    'mhwp_username': mhwp,
                    'Date': current_date.strftime("%Y/%m/%d"),
                    'Day': current_date.strftime("%A")
                }
                for col in templates_df.columns:
                    if '(' in col:
                        schedule_entry[col] = day_template[col]
                new_schedules.append(schedule_entry)
            current_date += timedelta(days=1)
    
    # Convert to DataFrame, remove duplicates keeping latest entry
    final_schedules = pd.DataFrame(new_schedules)
    # Sort by date first to ensure newest entries are kept
    final_schedules['Date'] = pd.to_datetime(final_schedules['Date'])
    final_schedules = final_schedules.sort_values('Date')
    # Keep last occurrence (newest) when dropping duplicates
    final_schedules = final_schedules.drop_duplicates(
        subset=['mhwp_username', 'Date'], 
        keep='last'
    )
    # Format date back to string
    final_schedules['Date'] = final_schedules['Date'].dt.strftime('%Y/%m/%d')

    # Save sorted schedules
    final_schedules.to_csv(schedule_file, index=False)
    print("\nSchedule updated successfully!")
    return True
