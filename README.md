# Healthcare Grants Explorer

A web page for filtering healthcare funding opportunities. This tool helps researchers find relevant grants across health workforce, digital health, healthcare technology, and innovation domains.


## Project Structure

```
healthcare-grants-explorer/
├── index.html             # Main grants explorer interface
├── info.html              # Funding sources information page
├── style.css              # Complete styling for both pages
├── app.js                 # Main application logic and functionality
├── data.csv               # Primary grants database (120+ opportunities)
├── tag_analysis.py        # Python script for tag frequency analysis
├── complexity.py          # Utility for complexity level mapping
├── info.md               # Source content for information page
└── README.md             # This file
```

## Technology Stack

- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Styling**: CSS Grid, Flexbox, CSS Custom Properties
- **Animation**: Canvas API for aurora effects, CSS transitions
- **Data**: CSV parsing and manipulation
- **Analytics**: Python for data analysis and tag generation


## Funding Categories

### **Australian Government**
- NHMRC (National Health and Medical Research Council)
- MRFF (Medical Research Future Fund)
- ARC (Australian Research Council)
- State and territory health innovation funds

### **International Foundations**
- Wellcome Trust
- Bill & Melinda Gates Foundation
- Chan Zuckerberg Initiative
- Open Philanthropy

### **Development Organisations**
- World Bank health initiatives
- Asian Development Bank programs
- UN agencies (WHO, UNICEF, UNDP)

### **Collaborative Programs**
- Horizon Europe (EU)
- NIH international collaborations
- Bilateral research partnerships


## Contributing

We welcome contributions to improve the Healthcare Grants Explorer! Here's how you can help:

### **Adding New Grants**
1. Update `data.csv` with new funding opportunities
2. Ensure all required fields are populated
3. Run `tag_analysis.py` to update tag frequencies
4. Test filtering and display functionality




<div align="center">

**Built with ❤️ for the healthcare research community at DHCRC**

*Last Updated: August 2025*

</div>