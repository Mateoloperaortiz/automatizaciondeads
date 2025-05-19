const { Client } = require('pg');
require('dotenv').config({ path: '../.env' });

async function updateJobStatus() {
  const client = new Client({
    connectionString: process.env.POSTGRES_URL,
  });

  try {
    await client.connect();
    console.log('Connected to PostgreSQL database');

    const updateQuery = `
      UPDATE job_ads 
      SET 
        status = 'scheduled', 
        schedule_start = NOW() - INTERVAL '1 hour',
        updated_at = NOW(),
        platforms_meta_enabled = true
      WHERE id = 2
      RETURNING *;
    `;

    const result = await client.query(updateQuery);
    
    if (result.rows.length > 0) {
      console.log('Successfully updated JobAd:', result.rows[0]);
    } else {
      console.log('No JobAd found with ID 2');
    }
  } catch (error) {
    console.error('Error updating JobAd:', error);
  } finally {
    await client.end();
    console.log('Disconnected from PostgreSQL database');
  }
}

updateJobStatus();
