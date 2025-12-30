// Temporary fix script for DoctorDashboard.js
const fs = require('fs');

const filePath = 'd:/AIML/AIML_lab_project/frontend/src/components/DoctorDashboard.js';
let content = fs.readFileSync(filePath, 'utf8');

// Fix HTML entities
content = content.replace(/&amp; gt;/g, '>');
content = content.replace(/&amp; lt;/g, '<');
content = content.replace(/=&amp; gt;/g, '=>');

fs.writeFileSync(filePath, content, 'utf8');
console.log('Fixed HTML entities in DoctorDashboard.js');
