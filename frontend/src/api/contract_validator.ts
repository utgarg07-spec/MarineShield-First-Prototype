import { isValidEPSG4326GeoJSON } from '../map/MapContainer';
import { mockSpillDetection, mockInvestigationResult, mockCounterfactualResult } from './clients/MockApiClient';

export function runDataContractValidation(): boolean {
  console.log('Running Person 1 Data Contract Assertions...');

  if (mockSpillDetection.status !== 'OIL_DETECTED') throw new Error('Spill status mismatch');
  if (mockSpillDetection.severity.severity_class !== 'MODERATE') throw new Error('Severity class mismatch');
  if (mockSpillDetection.lookalike_verification.predicted_class !== 'PETROLEUM_OIL') throw new Error('Lookalike class mismatch');
  if (mockSpillDetection.severity.explicit_non_claims.length === 0) throw new Error('Explicit non-claims missing');
  
  if (mockInvestigationResult.attribution_status !== 'SOURCE_UNKNOWN') throw new Error('Attribution status mismatch');
  if (mockInvestigationResult.unknown_trigger_reason !== 'PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED') throw new Error('Unknown trigger reason missing');
  if (!mockInvestigationResult.non_guilt_clause.includes('analytical investigation flags only')) throw new Error('Non-guilt clause missing');

  if (mockCounterfactualResult.status !== 'SUCCESS') throw new Error('Counterfactual status mismatch');
  if (mockCounterfactualResult.counterfactual_attribution_status !== 'SOURCE_UNKNOWN') throw new Error('Counterfactual attribution mismatch');
  if (mockCounterfactualResult.rank_changes[0].score_change !== -48.89) throw new Error('Score change mismatch');

  const validPolygon = {
    type: 'Polygon',
    coordinates: [[[73.18, 18.48], [73.22, 18.48], [73.22, 18.52], [73.18, 18.52], [73.18, 18.48]]]
  };
  const invalidLonPolygon = {
    type: 'Polygon',
    coordinates: [[[200.0, 18.48], [73.22, 18.48], [73.22, 18.52], [200.0, 18.52], [200.0, 18.48]]]
  };
  const malformedGeometry = { type: 'Invalid' };

  if (!isValidEPSG4326GeoJSON(validPolygon)) throw new Error('Valid EPSG:4326 GeoJSON failed validation');
  if (isValidEPSG4326GeoJSON(invalidLonPolygon)) throw new Error('Invalid EPSG:4326 GeoJSON passed validation');
  if (isValidEPSG4326GeoJSON(malformedGeometry)) throw new Error('Malformed GeoJSON passed validation');
  if (isValidEPSG4326GeoJSON(null)) throw new Error('Null GeoJSON passed validation');

  console.log('All Person 1 Data Contract Assertions Passed Successfully!');
  return true;
}
