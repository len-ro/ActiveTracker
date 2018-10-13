package ro.len.activeTracker;

import org.json.JSONException;
import org.json.JSONObject;

public class Event {
	private int id;
	private String name;
	private String code;
	
	public Event(JSONObject event){
		try {
			id = event.getInt("id");
			name = event.getString("name");
			code = event.getString("code");
		} catch (JSONException e) {
			e.printStackTrace();
		}
	}
	
	public Event(int id, String name, String code) {
		this.id = id;
		this.name = name;
		this.code = code;
	}

	/**
	 * @return the id
	 */
	public int getId() {
		return id;
	}

	/**
	 * @param id the id to set
	 */
	public void setId(int id) {
		this.id = id;
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}

	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}

	/**
	 * @return the code
	 */
	public String getCode() {
		return code;
	}

	/**
	 * @param code the code to set
	 */
	public void setCode(String code) {
		this.code = code;
	}

	@Override
	public String toString() {
		return getName();
	}
}
